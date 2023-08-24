from setuptools import setup

setup(
    name="intake-es",
    version="0.0.1",
    install_requires=[
        "xarray",
        "xarray-datatree",
        "pandas",
        "elasticsearch",
        "intake",
        "pandas",
    ],
    package_dir={"": "src"},
    include_package_data=True,
    entry_points={
        "console_scripts": ["catalog-generator = intake_es.generator:main"],
        "intake.drivers": ["es_cat = intake_es.catalog:ElasticSearchCatalog"],
        "intake.catalogs": [
            "local = intake_es.catalog:cat",
        ],
    },
)
