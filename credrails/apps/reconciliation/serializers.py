import codecs
import csv

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from credrails.apps.reconciliation.utils import CellId
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
            return {
                "column_positions": {col_name: position for position, col_name in enumerate(reader.fieldnames, start=1)},
                "data": {
                    row[record_id.lower()]: (index, row)
                    for index, row in enumerate(reader, start=2)  # starting at 2 because 1 is headers
                },
            }

    def validate_target(self, value):
        return self.validate_source(value=value)

    def to_representation(self, instance):
        discrepancies = []
        records_missing_in_source = []
        records_missing_in_target = []

        source = instance["source"]
        source_data, source_column_positions = source["data"], source["column_positions"]
        target = instance["target"]
        target_data, _ = target["data"], target["column_positions"]

        for key, value in source_data.items():
            if key not in target_data:
                row_number, data = value
                records_missing_in_target.append(data)

        for key, value in target_data.items():
            row_number, data = value
            source_value = source_data.get(key)
            if source_value is None:
                records_missing_in_source.append(data)
                continue

            target_source_row_number, target_source_data = source_value
            for column_name, column_value in data.items():
                if target_source_data[column_name] == column_value:
                    continue

                if target_source_data[column_name].lower() == column_value.lower():
                    cell_id = CellId(
                        row_number=target_source_row_number,
                        column_number=source_column_positions[column_name],
                    )
                    discrepancies.append(
                        {
                            "spreadsheet_cell_id": str(cell_id),
                            "column_name": column_name,
                            "row_number": target_source_row_number,
                            "reason": "Mismatching case",
                        }
                    )

        instance["records_missing_in_source"] = records_missing_in_source
        instance["records_missing_in_target"] = records_missing_in_target
        instance["discrepancies"] = discrepancies
        return super().to_representation(instance)
