import os
import fsspec
import intake
import elasticsearch
import logging
import pandas as pd
import xcdat
import xarray as xr
from intake.catalog.base import Catalog
from intake.catalog.utils import reload_on_change
from intake.source.base import DataSourceBase, Schema

logger = logging.getLogger("intake_es")


class ESCatalogError(Exception):
    pass


class NoResultError(ESCatalogError):
    pass


class ESXarraySource(DataSourceBase):
    container = "xarray"
    name = "es-xarray"

    def __init__(
        self, urlpath, xarray_kwargs=None, storage_options=None, metadata=None
    ):
        super().__init__(metadata=metadata)

        self._xarray_kwargs = xarray_kwargs or {}
        self._storage_options = storage_options or {}

        if "chunks" not in self._xarray_kwargs:
            self._xarray_kwargs["chunks"] = "auto"

        self._urlpath = urlpath
        self._ds = None
        self._schema = None

    def _get_schema(self):
        if self._ds is None:
            url = fsspec.open_local(self._urlpath, **self._storage_options)

            xr_kwargs = self._xarray_kwargs.copy()
            use_xcdat = xr_kwargs.pop("xcdat", False)

            if use_xcdat:
                self._ds = xcdat.open_mfdataset(url, **xr_kwargs)
            else:
                self._ds = xr.open_mfdataset(url, **xr_kwargs)

            metadata = {
                "dims": dict(self._ds.dims),
                "data_vars": {
                    k: list(self._ds[k].coords) for k in self._ds.data_vars.keys()
                },
                "coords": tuple(self._ds.coords.keys()),
            }

            metadata.update(self._ds.attrs)

            self._schema = Schema(
                datashape=None,
                dtype=None,
                shape=None,
                npartitions=None,
                extra_metadata=metadata,
            )

        return self._schema

    def read(self):
        self._load_metadata()
        return self._ds.load()

    def read_chunked(self):
        self._load_metadata()
        return self._ds

    def to_dask(self):
        return self.read_chunked()

    def to_xarray(self):
        return self.read_chunked()

    def to_xcdat(self):
        self._xarray_kwargs["xcdat"] = True
        return self.read_chunked()

    def _close(self):
        if sel._ds is not None:
            self._ds.close()


class ElasticSearchCatalog(Catalog):
    name = "elasticsearch"
    container = "catalog"
    auth = None

    def __init__(
        self,
        index,
        *,
        host=None,
        es_kwargs=None,
        xarray_kwargs=None,
        skip_client=False,
        **intake_kwargs,
    ):
        super().__init__(**intake_kwargs)

        self._index = index
        self._host = host
        self._es_kwargs = es_kwargs or {}
        self._xarray_kwargs = xarray_kwargs or {}

        if not skip_client:
            self._client = elasticsearch.Elasticsearch(self._host, **self._es_kwargs)

        self._df = None
        self._sort = [{"_doc": "asc"}]

    @property
    def df(self):
        return self._df

    @df.setter
    def df(self, df):
        self._df = df

        # Remove entries
        if self._df is not None:
            keys = set(
                [".".join(x.values[:-1].tolist()) for _, x in self._df.iterrows()]
            )
            for key in set(self._entries.keys()) - keys:
                del self._entries[key]

    @property
    def fields(self):
        mapping = self._client.indices.get_mapping(index=self._index)

        return list(mapping[self._index]["mappings"]["properties"])

    def count(self):
        if self._df is None:
            result = self._client.count(index=self._index, query={"match_all": {}})

            count = result["count"]
        else:
            count = len(self._df)

        return count

    def top(self, field):
        aggs = {"top": {"terms": {"field": "variable_id"}}}

        result = self._aggregation(aggs)

        data = [[x["key"], x["doc_count"]] for x in result["top"]["buckets"]]

        return pd.DataFrame(data, columns=[field, "count"])

    def search(self, **kwargs):
        if self._df is None:
            df = self._search_es(**kwargs)
        else:
            df = self._search_df(**kwargs)

        cat = self(xarray_kwargs=self._xarray_kwargs, skip_client=True)

        cat._df = df

        cat._client = self._client

        return cat

    def __call__(self, xarray_kwargs=None, **kwargs):
        if xarray_kwargs is not None:
            xr_kwargs = self._xarray_kwargs.copy()
            xr_kwargs.update(xarray_kwargs)

            kwargs["xarray_kwargs"] = xr_kwargs

        cat = super().__call__(**kwargs)

        cat._df = self._df

        cat._client = self._client

        return cat

    def _search_es(self, **kwargs):
        query = self._build_es_query(**kwargs)

        data, search_after = self._search(query)

        while True:
            try:
                new_data, search_after = self._search(query, search_after=search_after)
            except ESCatalogError:
                break

            data += new_data

        return pd.DataFrame([x["_source"] for x in data])

    def _build_es_query(self, **kwargs):
        if len(kwargs) == 0:
            query = {"match_all": {}}
        else:
            must_terms = []
            filter_terms = []
            must_not_terms = []

            for k, v in kwargs.items():
                if isinstance(v, (list, set)):
                    v = list(v)

                    negated = [x[1:] for x in v if x.startswith("!")]
                    filtered = [x for x in v if not x.startswith("!")]

                    if len(negated) > 0:
                        must_not_terms.append({"terms": {k: negated}})

                    if len(filtered) > 0:
                        filter_terms.append({"terms": {k: filtered}})
                else:
                    if v.startswith("!"):
                        must_not_terms.append({"term": {k: v[1:]}})
                    else:
                        must_terms.append({"term": {k: v}})

            query = {
                "bool": {
                    "must": must_terms,
                    "filter": filter_terms,
                    "must_not": must_not_terms,
                }
            }

        return query

    def _search(self, query, **kwargs):
        result = self._client.search(
            index=self._index, query=query, sort=self._sort, size=10000, **kwargs
        )

        data = result["hits"]["hits"]

        try:
            search_after = data[-1]["sort"]
        except IndexError:
            raise NoResultError("No results found") from None

        return data, search_after

    def _aggregation(self, aggs, **kwargs):
        result = self._client.search(index=self._index, aggs=aggs, size=0, **kwargs)

        return result["aggregations"]

    def _search_df(self, **kwargs):
        query = None

        for k, v in kwargs.items():
            if isinstance(v, (list, set)):
                v = list(v)
            else:
                v = list([v])

            term = None

            for x in v:
                try:
                    if x.startswith("!"):
                        y = self._df[k] != x[1:]
                    else:
                        y = self._df[k] == x
                except AttributeError:
                    raise ESCatalogError(
                        f"Could not search values {v!r} in {k!r}"
                    ) from None

                if term is None:
                    term = y
                else:
                    term |= y

            if query is None:
                query = term
            else:
                query &= term

        return self._df[query].reset_index(drop=True)

    @reload_on_change
    def _get_entries(self):
        if self._df is None:
            return self._entries

        self._entries = {
            ".".join(x.values[:-1].tolist()): ESXarraySource(
                f"{x['path']}/*.nc",
                xarray_kwargs=self._xarray_kwargs,
                storage_options=self.storage_options,
            )
            for _, x in self._df.iterrows()
        }

        return self._entries

    def __getitem__(self, key):
        return self._entries[key]

    def __repr__(self):
        return f"<{self._index} catalog with {len(self)} datasets>"

    def _repr_html_(self):
        if self._df is None:
            return f"<p><strong>{repr(self)}</strong></p>"

        return self._df._repr_html_()

    def _ipython_display_(self):
        from IPython.display import HTML, display

        display(HTML(self._repr_html_()))

    def _ipython_key_completions_(self):
        return list(self)

    def _close(self):
        if self._client:
            self._client.close()

            del self._client

            self._client = None

    def __del__(self):
        self._close()

    def to_dataset_dict(self, xcdat=False):
        if xcdat:
            ds_dict = {x: self[x].to_xcdat() for x in list(self)}
        else:
            ds_dict = {x: self[x].to_xarray() for x in list(self)}

        return ds_dict

    def to_datatree(self, xcdat=False):
        try:
            from datatree import DataTree
        except ImportError:
            raise Exception("Please install the xarray-datatree package")

        datasets = self.to_dataset_dict(xcdat=xcdat)

        datasets = {x.replace(".", "/"): y for x, y in datasets.items()}

        return DataTree.from_dict(datasets)


p = os.path.abspath(os.path.dirname(__file__))
cat = intake.open_catalog(os.path.join(p, "local.yaml"))
