"""Conservative compatibility analysis of explicitly supported OpenAPI shapes."""

METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}


def analyze(before, after):
    if (
        not isinstance(before, dict)
        or not isinstance(after, dict)
        or any(
            not str(doc.get("openapi", "")).startswith("3.") for doc in [before, after]
        )
    ):
        raise ValueError("Two OpenAPI 3 documents are required")
    changes = []
    unsupported = []

    def emit(kind, location, message):
        changes.append({"kind": kind, "location": location, "message": message})

    def inspect(value, path):
        if isinstance(value, dict):
            for key, child in value.items():
                if key in [
                    "allOf",
                    "oneOf",
                    "anyOf",
                    "$ref",
                    "not",
                    "minimum",
                    "maximum",
                    "exclusiveMinimum",
                    "exclusiveMaximum",
                    "minLength",
                    "maxLength",
                    "pattern",
                    "minItems",
                    "maxItems",
                    "additionalProperties",
                    "nullable",
                    "discriminator",
                ]:
                    unsupported.append(
                        {
                            "location": path + "/" + key,
                            "reason": "This schema feature requires manual review",
                        }
                    )
                inspect(child, path + "/" + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                inspect(child, path + "/" + str(index))

    for label, doc in [("before", before), ("after", after)]:
        inspect(doc, label)
    for path, definition in before.get("paths", {}).items():
        target = after.get("paths", {}).get(path, {})
        for method, operation in definition.items():
            if method not in METHODS:
                continue
            location = method.upper() + " " + path
            if method not in target:
                emit("breaking", location, "Operation removed")
                continue
            new = target[method]
            old_parameters = {
                (p.get("in"), p.get("name")): p
                for p in definition.get("parameters", [])
                + operation.get("parameters", [])
                if "$ref" not in p
            }
            new_parameters = {
                (p.get("in"), p.get("name")): p
                for p in target.get("parameters", []) + new.get("parameters", [])
                if "$ref" not in p
            }
            for key, param in new_parameters.items():
                old = old_parameters.get(key)
                if param.get("required", False) and (
                    not old or not old.get("required", False)
                ):
                    emit("breaking", location, "Required parameter added: " + str(key))
                if old:
                    compare_schema(
                        old.get("schema", {}),
                        param.get("schema", {}),
                        location + " parameter " + str(key),
                        emit,
                        "input",
                    )
            if new.get("requestBody", {}).get("required", False) and not operation.get(
                "requestBody", {}
            ).get("required", False):
                emit("breaking", location, "Request body became required")
            old_body = operation.get("requestBody", {}).get("content", {})
            new_body = new.get("requestBody", {}).get("content", {})
            for media, content in old_body.items():
                if media not in new_body:
                    emit(
                        "breaking",
                        location,
                        "Accepted request media type removed: " + media,
                    )
                else:
                    compare_schema(
                        content.get("schema", {}),
                        new_body[media].get("schema", {}),
                        location + " body " + media,
                        emit,
                        "input",
                    )
            for code, response in operation.get("responses", {}).items():
                if code not in new.get("responses", {}):
                    emit("breaking", location, "Response removed: " + code)
                    continue
                new_content = new["responses"][code].get("content", {})
                for media, content in response.get("content", {}).items():
                    if media not in new_content:
                        emit(
                            "breaking",
                            location,
                            "Response media type removed: " + media,
                        )
                    else:
                        compare_schema(
                            content.get("schema", {}),
                            new_content[media].get("schema", {}),
                            location + " response " + code,
                            emit,
                            "output",
                        )
    old_schemas = before.get("components", {}).get("schemas", {})
    new_schemas = after.get("components", {}).get("schemas", {})
    for name, schema in old_schemas.items():
        if name not in new_schemas:
            emit("breaking", "schema " + name, "Component schema removed")
        else:
            compare_schema(schema, new_schemas[name], "schema " + name, emit, "unknown")
    return {
        "breaking": sum(c["kind"] == "breaking" for c in changes),
        "changes": changes,
        "unsupported": unsupported,
        "fully_analyzed": not unsupported,
    }


def compare_schema(old, new, location, emit, direction):
    if old.get("type") != new.get("type"):
        emit("breaking", location, "Schema type changed")
    if old.get("format") != new.get("format"):
        emit("breaking", location, "Schema format changed")
    if "enum" in old or "enum" in new:
        previous = set(map(str, old.get("enum", [])))
        current = set(map(str, new.get("enum", [])))
        narrowed = "enum" in new and ("enum" not in old or bool(previous - current))
        expanded = "enum" in old and ("enum" not in new or bool(current - previous))
        if (direction != "output" and narrowed) or (direction != "input" and expanded):
            emit("breaking", location, "Enum compatibility changed")
    required_old = set(old.get("required", []))
    required_new = set(new.get("required", []))
    if direction != "output" and required_new - required_old:
        emit(
            "breaking",
            location,
            "New required properties: "
            + ", ".join(sorted(required_new - required_old)),
        )
    if direction != "input" and required_old - required_new:
        emit("breaking", location, "Required response properties became optional")
    for key, property_schema in old.get("properties", {}).items():
        if key not in new.get("properties", {}):
            emit("breaking", location + "." + key, "Property removed")
        else:
            compare_schema(
                property_schema,
                new["properties"][key],
                location + "." + key,
                emit,
                direction,
            )
    if "items" in old and "items" in new:
        compare_schema(old["items"], new["items"], location + "[]", emit, direction)


def markdown(report):
    from html import escape

    def safe(value):
        return escape(str(value)).replace("|", r"\|").replace("\n", " ")

    lines = [
        "# API compatibility report",
        "",
        f"Breaking findings: {report['breaking']}",
        f"Fully analyzed: {report['fully_analyzed']}",
        "",
        "| Kind | Location | Finding |",
        "| --- | --- | --- |",
    ]
    for change in report["changes"]:
        lines.append(
            "| "
            + safe(change["kind"])
            + " | "
            + safe(change["location"])
            + " | "
            + safe(change["message"])
            + " |"
        )
    for item in report["unsupported"]:
        lines.append(
            "| Review | " + safe(item["location"]) + " | " + safe(item["reason"]) + " |"
        )
    return "\n".join(lines) + "\n"
