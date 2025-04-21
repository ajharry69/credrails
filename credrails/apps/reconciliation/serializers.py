import codecs
import csv
import re
from collections import namedtuple

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from credrails.apps.reconciliation.utils import CellId
from credrails.apps.reconciliation.validators import FileMimeTypeValidator

ValidData = namedtuple("ValidData", ["data", "column_positions"])
RecordValue = namedtuple("RecordValue", ["row_number", "data"])


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
            return ValidData(
                data={
                    row[record_id.lower()]: RecordValue(row_number=index, data=row)
                    for index, row in enumerate(reader, start=2)  # starting at 2 because 1 is headers
                },
                column_positions={col_name: position for position, col_name in enumerate(reader.fieldnames, start=1)},
            )

    def validate_target(self, value):
        return self.validate_source(value=value)

    def to_representation(self, instance):
        discrepancies = []
        records_missing_in_source = []

        source: ValidData = instance["source"]
        target: ValidData = instance["target"]

        for key, value in target.data.items():
            source_value: RecordValue = source.data.get(key)
            if source_value is None:
                records_missing_in_source.append(value.data)
                continue

            for column_name, column_value in value.data.items():
                if source_value.data[column_name] == column_value:
                    continue

                reason = "Mismatching date format"  # assume we are looking at a date as the last resort

                if source_value.data[column_name].lower() == column_value.lower():
                    reason = "Mismatching case"
                elif re.match(r"^\d+(\.\d+)?$", column_value):
                    if float(source_value.data[column_name]) == float(column_value):
                        continue

                    reason = "Mismatching numbers"

                cell_id = CellId(
                    row_number=source_value.row_number,
                    column_number=source.column_positions[column_name],
                )
                discrepancy = {
                    "spreadsheet_cell_id": str(cell_id),
                    "column_name": column_name,
                    "row_number": source_value.row_number,
                    "reason": reason,
                }
                discrepancies.append(discrepancy)

        instance["discrepancies"] = discrepancies
        instance["records_missing_in_source"] = records_missing_in_source
        instance["records_missing_in_target"] = [v.data for k, v in source.data.items() if k not in target.data]
        return super().to_representation(instance)
