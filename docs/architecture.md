# Contract Diff Analyzer: architecture

## Conservative compatibility reporting

The analyzer compares operations, parameters, request-body requirements, response content and component properties. Input enum narrowing and output enum expansion are treated differently. Reports identify location and reason; the optional gate returns failure for breaking changes or unsupported features.

## Module boundaries

`contract_diff_analyzer/core.py` contains the algorithm and persistence operations. `cli.py` validates arguments and prints JSON. The package entrypoint translates input and storage errors into structured stderr with exit status 2. Domain-specific unsuccessful results can use exit status 1. There is no shared runtime dependency on the portfolio folder.

## Failure and operational boundaries

References, composition and unsupported constraints require manual review. fully_analyzed means the documented subset was analyzed, not formal proof of compatibility. Structural malformed inputs fail rather than produce a safe verdict. This tool intentionally does not resolve external references or execute schemas.

## Verification

Core tests cover valid results and failure boundaries. Process-level CLI tests run the committed examples in temporary copies, inspect JSON output and verify domain outcomes. CI runs on Python 3.11 and 3.13, Linux and Windows, checks package installation, and builds and executes the non-root Docker image.

## Extension choices

The standard-library implementation keeps local execution inspectable and offline. A hosted or distributed version would require workload-specific authorization, resource limits, durable coordination and observability. Extend the core through tested functions rather than adding infrastructure without a scaling requirement.
