from unittest import mock

import pytest
from django.core.exceptions import ValidationError

from credrails.apps.reconciliation.validators import FileMimeTypeValidator


class TestFileMimeTypeValidator:
    @pytest.mark.parametrize(
        "allowed_mime_types",
        [
            ["csv"],
            ["TEXT"],
            ["TEXT/"],
            ["/csv"],
            ["/"],
        ],
    )
    def test_init_should_raise_exception(self, allowed_mime_types):
        with pytest.raises(ValueError, match="Invalid mime type"):
            FileMimeTypeValidator(allowed_mime_types=allowed_mime_types)

    @pytest.mark.parametrize(
        "allowed_mime_types, expected_allowed_mime_types",
        [
            (None, None),
            ([], []),
            (["TEXT/csv"], ["text/csv"]),
            (["TEXT/CSV"], ["text/csv"]),
            (["TeXT/CSV"], ["text/csv"]),
            (["TeXT/CSv"], ["text/csv"]),
            (["text/csv"], ["text/csv"]),
        ],
    )
    def test_init_should_not_raise_exception(self, allowed_mime_types, expected_allowed_mime_types):
        validator = FileMimeTypeValidator(allowed_mime_types=allowed_mime_types)

        assert validator.allowed_mime_types == expected_allowed_mime_types

    @pytest.mark.parametrize(
        "allowed_mime_types, value_content_type",
        [
            ([], "text/csv"),
            (["text/csv"], "application/json"),
        ],
    )
    def test_call_should_raise_exception(self, allowed_mime_types, value_content_type):
        value = mock.MagicMock()
        value.content_type = value_content_type

        validator = FileMimeTypeValidator(allowed_mime_types=allowed_mime_types)

        with pytest.raises(ValidationError):
            validator(value=value)

    @pytest.mark.parametrize(
        "allowed_mime_types, value_content_type",
        [
            (["text/csv"], "text/csv"),
            (["text/csv", "application/json"], "text/csv"),
        ],
    )
    def test_call_should_not_raise_exception(self, allowed_mime_types, value_content_type):
        value = mock.MagicMock()
        value.content_type = value_content_type

        validator = FileMimeTypeValidator(allowed_mime_types=allowed_mime_types)

        actual = validator(value=value)

        assert actual is None
