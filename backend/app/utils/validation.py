from marshmallow import Schema, ValidationError
from flask import jsonify


def validate_or_400(schema: Schema, data: dict):
    """
    Validates `data` against `schema`.
    Returns (clean_data, None) on success.
    Returns (None, error_response) on failure.

    Usage in a route:
        data, err = validate_or_400(CreateProjectSchema(), request.get_json(silent=True) or {})
        if err:
            return err
        # use data['name'] etc.
    """
    try:
        clean = schema.load(data)
        return clean, None
    except ValidationError as exc:
        # Flatten marshmallow's nested error dict into a readable list
        messages = _flatten_errors(exc.messages)
        return None, (jsonify({"error": "Validation failed", "fields": messages}), 422)


def _flatten_errors(errors: dict, prefix: str = "") -> dict:
    """Recursively flattens {field: [msgs]} into {"field": "msg1; msg2"}."""
    flat = {}
    for field, value in errors.items():
        key = f"{prefix}.{field}" if prefix else field
        if isinstance(value, list):
            flat[key] = "; ".join(str(m) for m in value)
        elif isinstance(value, dict):
            flat.update(_flatten_errors(value, prefix=key))
    return flat
