import os
import json
import re
import subprocess
import itertools
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="Conda environment file")
    parser.add_argument("output-path", help="Output directory")

    kwargs = vars(parser.parse_args())

    categories = get_categories(**kwargs)

    search_args = "|".join(
        [f"^{x}$" for packages in categories.values() for x in packages]
    )

    output = subprocess.run(
        f"mamba list {search_args!r} --json",
        capture_output=True,
        shell=True
    )

    output_json = json.loads(output.stdout)

    versions = {
        package["name"]: package["version"] for package in output_json
    }

    table = []
    categories = list(categories.items())

    for i in range(0, len(categories), 3):
        header = " | ".join([x[0] for x in categories[i:i+3]])
        separator = " | ".join([f"{'-'*len(x[0])}" for x in categories[i:i+3]])
        header = f"| {header} |\n| {separator} |"

        rows = itertools.zip_longest(*[x[1] for x in categories[i:i+3]])
        rows = [
            " | ".join(
                [
                    "" if y is None else f"{y} {get_version(y, versions)}"
                    for y in x
                ]
            ) for x in rows
        ]
        rows = "\n".join(f"| {x} |" for x in rows)

        table.append(f"{header}\n{rows}\n")

    table = "\n".join(table)

    data = f"""# Packages

{table}"""

    output_path = os.path.join(kwargs["output-path"], "README.md")

    with open(output_path, "w") as fd:
        fd.write(data)


def get_version(package, versions):
    m = re.search(r"([^<>=]*)(?:(?:<|>|<=|>=|==).*)?", package)

    if m is None:
        raise Exception("Could not parse ", package)

    name = m.group(1)

    return versions[name]


def get_categories(file, **_):
    with open(file) as fd:
        lines = fd.readlines()

    category = None
    packages = {}

    for line in lines:
        if "#" in line:
            m = re.search("# (.*)(?: packages)?", line)

            if m is None:
                continue

            category = m.group(1)
        elif category != "ignore" and category is not None:
            m = re.search("- (.*)", line)

            if m is None:
                continue

            if category in packages:
                packages[category].append(m.group(1))
            else:
                packages[category] = [m.group(1)]

    return packages


if __name__ == "__main__":
    main()
