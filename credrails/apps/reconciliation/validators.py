import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class FileMimeTypeValidator:
    def __init__(self, allowed_mime_types=None):
        self.allowed_mime_types = None
        if allowed_mime_types is not None:
            mime_types = []
            for allowed_type in allowed_mime_types:
                if not re.match(r"\w+/\w+", allowed_type):
                    raise ValueError("Invalid mime type")
                mime_types.append(allowed_type.lower())
            self.allowed_mime_types = mime_types

    def __call__(self, value):
        mime_type = value.content_type.lower()
        if self.allowed_mime_types is not None and mime_type not in self.allowed_mime_types:
            raise ValidationError(
                _("File type “%(mime_type)s” is not allowed. Allowed types are: %(allowed_mime_types)s."),
                code="invalid_mime_type",
                params={
                    "mime_type": mime_type,
                    "allowed_mime_types": ", ".join(self.allowed_mime_types),
                    "value": value,
                },
            )
