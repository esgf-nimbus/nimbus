import os
import argparse
import elasticsearch as es
import subprocess
import pandas as pd
import tempfile
import warnings
from elasticsearch.helpers import bulk
from dask.delayed import delayed
from distributed import Client
from dask.distributed import progress
from pathlib import Path

warnings.filterwarnings("ignore")


def list_dirs(p, root, depth, current=0):
    dirs = [(x, root) for x in p.iterdir() if x.is_dir()]

    if depth == current + 1:
        return dirs
    else:
        child_dirs = []
        for x in dirs:
            child_dirs += list_dirs(x[0], root, depth, current + 1)
        return child_dirs


def find_dirs(p, root, tmp, headers):
    filename = "_".join(str(p).split("/")[1:])

    result = subprocess.run(
        f"find {p!s} -type d -links 2", shell=True, capture_output=True
    )

    values = result.stdout.decode("utf-8").strip().split("\n")

    data = []

    for x in values:
        try:
            relative = Path(x).relative_to(root)
        except Exception:
            continue
        v = str(relative).split("/")
        if len(v) == len(headers):
            data.append(
                v
                + [
                    x,
                ]
            )

    df = pd.DataFrame(
        data,
        columns=headers
        + [
            "path",
        ],
    )

    df.to_csv(Path(tmp, f"{filename}.csv"))


def execute(client, delayed_funcs):
    futures = client.compute(delayed_funcs)

    progress(futures)

    client.gather(futures)


def load_results(tmp):
    data = []

    for x in os.listdir(tmp):
        data.append(pd.read_csv(f"{tmp}/{x}", index_col=0))

    return pd.concat(data).reset_index(drop=True)


def index_results(url, username, password, name, df, remove=False):
    client = es.Elasticsearch(url, verify_certs=False, basic_auth=(username, password))

    if remove:
        try:
            client.indices.delete(index=name)
        except Exception:
            pass

    try:
        client.indices.create(
            index=name,
            mapping={
                "properties": {x: {"type": "keyword"} for x in df.columns[1:]},
            },
        )
    except Exception:
        pass

    def gendata():
        columns = df.columns.tolist()

        for x in df.values.tolist():
            data = {k: v for k, v in zip(columns, x)}
            doc = {"_index": name, "_source": data}
            yield doc

    result = bulk(client, gendata(), raise_on_error=False)

    print(result)


def main():
    parser = argparse.ArgumentParser(prog="catalog")

    parser.add_argument("name")
    parser.add_argument("--root", nargs="+", required=True)
    parser.add_argument("--headers", nargs="+", required=True)
    parser.add_argument("--depth", required=True, type=int)
    parser.add_argument("--workers", required=True, type=int)
    parser.add_argument("--threads", required=True, type=int)
    parser.add_argument("--output", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    parser.add_argument("--remove", required=True, action="store_true")

    args = parser.parse_args()

    roots = [Path(x) for x in args.root]
    roots = [y for x in roots for y in list_dirs(x, x.parent, args.depth)]

    output = Path(args.output)

    if output.exists():
        df = pd.read_csv(output, index_col=0)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            delayed_find_dirs = [
                delayed(find_dirs)(x, y, tmp, args.headers) for x, y in roots
            ]

            with Client(
                n_workers=args.workers, threads_per_worker=args.threads
            ) as client:
                execute(client, delayed_find_dirs)

            df = load_results(tmp)

        df.to_csv(args.output)

    index_results(
        args.url, args.username, args.password, args.name, df, remove=args.remove
    )


if __name__ == "__main__":
    main()
