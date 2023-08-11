import os
import intake
import elasticsearch
import logging
import warnings
import pandas as pd
from intake_xarray.netcdf import NetCDFSource

logging.basicConfig(level=logging.DEBUG)


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

    def search(self, **kwargs):
        """Search the Elasticsearch index.

        The values of the search arguments can be a string or list. If a list
        the each value must be present to match.

        Args:
            kwargs: Search arguments.

        Examples:
            >>> cat.search(activity_drs='ScenarioMIP', variable_id=['pr', 'tas'])
        """
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

            for k, v in self._search_kwargs.items():
                if isinstance(v, (list, set)):
                    filter_terms.append({"terms": {k: v}})
                else:
                    must_terms.append({"term": {k: v}})

            query = {
                "bool": {
                    "must": must_terms,
                    "filter": filter_terms,
                }
            }

        logging.debug(f"Using query {query}")

        sort = [{"_doc": "asc"}]
        result = self._client.search(
            index=self._index, query=query, sort=sort, size=10000
        )
        data = [x["_source"] for x in result["hits"]["hits"]]

        total_hits = result["hits"]["total"]["value"]
        relation = result["hits"]["total"]["relation"]

        if total_hits == 10000 and relation == "gte":
            logging.debug("Pulling additional documents")

            for idx in range(10):
                if len(result["hits"]["hits"]) == 0:
                    break
                search_after = result["hits"]["hits"][-1]["sort"]
                result = self._client.search(
                    index=self._index,
                    query=query,
                    sort=sort,
                    search_after=search_after,
                    size=10000,
                )
                data += [x["_source"] for x in result["hits"]["hits"]]

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
            ".".join(x.values[:-1].tolist()): NetCDFSource(f'{x["path"]}/*.nc')
            for _, x in df.iterrows()
        }

        return cat

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
        if self._df is None:
            return super().__repr__()
        return f"<{self._index} catalog with {len(self)} datasets>"

    def _repr_html_(self):
        if self._df is None:
            return super().__repr__()
        return self._df._repr_html_()

    def _ipython_display_(self):
        from IPython.display import HTML, display

        display(HTML(self._repr_html_()))

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

    def to_dataset_dict(self):
        if len(self) > 20:
            warnings.warn(
                "Opening more than 20 datasets, this may take awhile",
                ResourceWarning,
                stacklevel=2,
            )

        return {x: self[x].to_dask() for x in list(self)}

    def to_datatree(self):
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

        datasets = self.to_dataset_dict()

        datasets = {x.replace(".", "/"): y for x, y in datasets.items()}

        return DataTree.from_dict(datasets)


p = os.path.abspath(os.path.dirname(__file__))
cat = intake.open_catalog(os.path.join(p, "local.yaml"))
