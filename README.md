# Contract Diff Analyzer

Breaking-change analysis of a documented OpenAPI subset. An independent Python 3.11+ project using the standard library, with a real command-line interface and no runtime package dependencies.

## Run locally

From the cloned repository, run:

```sh
python -m contract_diff_analyzer compare examples/before.json examples/after.json
python -m contract_diff_analyzer compare examples/before.json examples/before.json --fail-on-breaking
python -m contract_diff_analyzer --help
```

Examples contain synthetic data. First use requires no cloud account, API key or package download. Optionally install the CLI using `python -m pip install .` and run `contract-diff-analyzer --help`.

## Verify

```sh
python -m unittest discover -v
```

GitHub Actions checks Python 3.11 and 3.13 on Linux and Windows, verifies package installation, and builds/runs the non-root Docker image.

```sh
docker build -t contract-diff-analyzer .
docker run --rm contract-diff-analyzer --help
```

Mount a working directory at `/workspace` to process your own files. The container runs as UID 10001; provide appropriate write permissions for outputs.

## Architecture and scope

Business algorithms live in `contract_diff_analyzer/core.py`; `contract_diff_analyzer/cli.py` owns argument parsing and JSON output. Tests exercise success cases and failure boundaries, with temporary storage for mutations. See [design decisions](docs/architecture.md).

Analyzes operation removal, parameters, request-body requirements, response removal and component property/type/enum changes. Unresolved references and composition schemas are reported as unsupported instead of assumed safe.

This project demonstrates implemented engineering practices. It does not claim production deployment history or external certifications.
