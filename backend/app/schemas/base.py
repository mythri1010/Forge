import re
from marshmallow import Schema, fields, validate, validates, ValidationError, pre_load

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class BaseSchema(Schema):
    """Strip extra whitespace from all string fields before validation."""

    @pre_load
    def strip_strings(self, data, **kwargs):
        if not isinstance(data, dict):
            return data
        return {
            k: v.strip() if isinstance(v, str) else v
            for k, v in data.items()
        }


class EmailField(fields.Email):
    def _deserialize(self, value, attr, data, **kwargs):
        value = super()._deserialize(value, attr, data, **kwargs)
        return value.lower()
