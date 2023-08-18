import os
import fsspec
import intake
import elasticsearch
import logging
import warnings
import pandas as pd
import xcdat
from intake_xarray.netcdf import NetCDFSource


class ESCatalogError(Exception):
    pass


class NoResultError(ESCatalogError):
    pass


class ESNetCDFSource(NetCDFSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_xcdat(self, **kwargs):
        if self._can_be_local:
            url = fsspec.open_local(self.urlpath, **self.storage_options)
        else:
            url = fsspec.open(self.urlpath, **self.storage_options).open()

        return xcdat.open_mfdataset(url, **kwargs)


class ElasticSearchCatalog(intake.Catalog):
    name = "elasticsearch"
    container = "xarray"
    auth = None

    def __init__(
        self,
        index,
        *,
        host=None,
        es_kwargs=None,
        search_kwargs=None,
        skip_client=False,
        **kwargs,
    ):
        """Elasticsearch intake catalog.

        Args:
            index: String name of the index to search.
            host: String url to the Elasticsearch cluster.
            es_kwargs: Dictionary of arguments to pass Elasticsearch client.
            search_kwargs: Dictionary of initial search arguments.
            skip_client: Bool to skip initializing the Elasticsearch client.
            kwargs: Extra arguments to pass to `intake.Catalog`.
        """
        super().__init__(**kwargs)

        self._index = index
        self._host = host
        self._es_kwargs = es_kwargs
        self._search_kwargs = search_kwargs

        if es_kwargs is None:
            es_kwargs = {}

        if not skip_client:
            self._client = elasticsearch.Elasticsearch(host, **es_kwargs)

        self._df = None
        self._entries = {}

    @property
    def describe_index(self):
        try:
            return self._client.indices.get(index=self._index).body
        except Exception:
            raise ESCatalogError("Unable to query information about the index")

    @property
    def fields(self):
        try:
            fields = {}
            for x, y in self.describe_index[self._index]["mappings"][
                "properties"
            ].items():
                try:
                    fields[x] = list(y["fields"].keys())[0]
                except KeyError:
                    fields[x] = y["type"]
            return fields
        except Exception:
            raise ESCatalogError("Unable to query field mapping for the index")

    @property
    def count(self):
        result = self._client.count(index=self._index)

        return result["count"]

    def field_top(self, field):
        aggs = {"unique": {"terms": {"field": field}}}

        result = self._client.search(index=self._index, aggs=aggs, size=0)

        data = result["aggregations"]["unique"]["buckets"]

        return {x["key"]: x["doc_count"] for x in data}

    def field_nunique(self, field):
        aggs = {
            "unique": {
                "composite": {"sources": {"values": {"terms": {"field": field}}}}
            }
        }

        result = self._client.search(index=self._index, aggs=aggs, size=0)

        data = result["aggregations"]["unique"]["buckets"]
        after_key = result["aggregations"]["unique"]["after_key"]

        while True:
            aggs["unique"]["composite"]["after"] = after_key
            result = self._client.search(index=self._index, aggs=aggs, size=0)

            new_data = result["aggregations"]["unique"]["buckets"]

            if len(new_data) == 0:
                break

            data += new_data
            after_key = result["aggregations"]["unique"]["after_key"]

        return {x["key"]["values"]: x["doc_count"] for x in data}

    def search(self, dry_run=False, **kwargs):
        """Search the Elasticsearch index.

        The values of the search arguments can be a string or list. If a list
        the each value must be present to match.

        Args:
            kwargs: Search arguments.

        Examples:
            >>> cat.search(activity_drs='ScenarioMIP', variable_id=['pr', 'tas'])
        """
        query = self._build_query(**kwargs)

        logging.debug(f"Built query {query}")

        if dry_run:
            result = self._client.count(index=self._index, query=query)

            logging.debug(f"Raw result {result}")

            return result["count"]
        else:
            logging.debug(f"Using query {query}")

            sort = [{"_doc": "asc"}]

            result = self._client.search(
                index=self._index, query=query, sort=sort, size=10000
            )
            data = result["hits"]["hits"]

            try:
                search_after = result["hits"]["hits"][-1]["sort"]
            except IndexError:
                raise ESCatalogError("No results found") from None

            while True:
                result = self._client.search(
                    index=self._index,
                    query=query,
                    sort=sort,
                    search_after=search_after,
                    size=10000,
                )

                new_data = result["hits"]["hits"]

                if len(new_data) == 0:
                    break

                search_after = new_data[-1]["sort"]

                data += new_data

            data = [x["_source"] for x in data]

            df = pd.DataFrame(data)

            cat = ElasticSearchCatalog(
                self._index,
                host=self._host,
                es_kwargs=self._es_kwargs,
                search_kwargs=self._search_kwargs,
                skip_client=True,
            )

            cat._df = df

            cat._entries = {
                ".".join(x.values[:-1].tolist()): ESNetCDFSource(f'{x["path"]}/*.nc')
                for _, x in df.iterrows()
            }

            return cat

    def _build_query(self, **kwargs):
        if len(kwargs) == 0:
            warnings.warn(
                "No search arguments, this may take awhile",
                ResourceWarning,
                stacklevel=2,
            )

            query = {"match_all": {}}
        else:
            if self._search_kwargs is None:
                self._search_kwargs = kwargs
            else:
                self._search_kwargs.update(kwargs)

            must_terms = []
            filter_terms = []
            must_not_terms = []

            for k, v in self._search_kwargs.items():
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

            query_bool = {}

            if len(must_terms) > 0:
                query_bool["must"] = must_terms

            if len(filter_terms) > 0:
                query_bool["filter"] = filter_terms

            if len(must_not_terms) > 0:
                query_bool["must_not"] = must_not_terms

            query = {"bool": query_bool}

        return query

    def keys(self):
        try:
            return [".".join(x.values[:-1].tolist()) for idx, x in self._df.iterrows()]
        except AttributeError:
            return []

    @property
    def df(self):
        return self._df

    def __len__(self):
        return len(self._entries)

    def __getitem__(self, key):
        return self._entries[key]

    def __repr__(self):
        return f"<{self._index} catalog with {len(self)} datasets>"

    def _repr_html_(self):
        if self._df is None:
            return f"<p><strong>{self._index} catalog with {len(self)} datasets</strong></p>"

        return self._df._repr_html_()

    def _ipython_display_(self):
        from IPython.display import HTML, display

        display(HTML(self._repr_html_()))

    def _ipython_key_completions_(self):
        return list(self)

    def _close(self):
        self._client.close()

        del self._client

        self._client = None

    def __del__(self):
        self._close()

        super().__del__()

    def unique(self):
        try:
            data = {x: self._df[x].unique().tolist() for x in self._df.columns[:-1]}
        except AttributeError:
            return {}

        return data

    def nunique(self):
        try:
            data = {x: self._df[x].nunique() for x in self._df.columns[:-1]}
        except AttributeError:
            return {}

        return data

    def to_dataset_dict(self, to_xcdat=False, **kwargs):
        if len(self) > 20:
            warnings.warn(
                "Opening more than 20 datasets, this may take awhile",
                ResourceWarning,
                stacklevel=2,
            )

        if to_xcdat:
            ds_dict = {x: self[x].to_xcdat(**kwargs) for x in list(self)}
        else:
            ds_dict = {x: self[x].to_dask() for x in list(self)}

        return ds_dict

    def to_datatree(self, **kwargs):
        try:
            from datatree import DataTree
        except ImportError:
            raise Exception("Please install the xarray-datatree package")

        if len(self) > 20:
            warnings.warn(
                "Opening more than 20 datasets, this may take awhile",
                ResourceWarning,
                stacklevel=2,
            )

        datasets = self.to_dataset_dict(**kwargs)

        datasets = {x.replace(".", "/"): y for x, y in datasets.items()}

        return DataTree.from_dict(datasets)


p = os.path.abspath(os.path.dirname(__file__))
cat = intake.open_catalog(os.path.join(p, "local.yaml"))
