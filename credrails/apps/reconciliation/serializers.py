import codecs
import csv

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from credrails.apps.reconciliation.validators import FileMimeTypeValidator


class ReconciliationSerializer(serializers.Serializer):
    source = serializers.FileField(write_only=True, validators=[FileMimeTypeValidator(allowed_mime_types=["text/csv"])])
    target = serializers.FileField(write_only=True, validators=[FileMimeTypeValidator(allowed_mime_types=["text/csv"])])
    records_missing_in_source = serializers.ListField(child=serializers.JSONField(), read_only=True)
    records_missing_in_target = serializers.ListField(child=serializers.JSONField(), read_only=True)
    discrepancies = serializers.ListField(child=serializers.JSONField(), read_only=True)

    def validate_source(self, value):
        with value as f:
            try:
                reader = csv.DictReader(codecs.iterdecode(f, "utf-8"))
            except csv.Error as e:
                raise ValidationError(detail="Invalid CSV data") from e

            record_id = reader.fieldnames[0]
            return {row[record_id.lower()]: row for row in reader}

    def validate_target(self, value):
        return self.validate_source(value=value)

    def to_representation(self, instance):
        discrepancies = []
        records_missing_in_source = []
        records_missing_in_target = []

        source = instance["source"]
        target = instance["target"]

        for key, value in source.items():
            if key not in target:
                records_missing_in_target.append(value)

        for key, value in target.items():
            if key not in source:
                records_missing_in_source.append(value)

        instance["records_missing_in_source"] = records_missing_in_source
        instance["records_missing_in_target"] = records_missing_in_target
        instance["discrepancies"] = discrepancies
        return super().to_representation(instance)
