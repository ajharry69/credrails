import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from credrails.apps.reconciliation.serializers import ReconciliationSerializer


class TestReconciliationSerializer:
    @staticmethod
    def csv_file(content):
        if content is not None:
            return SimpleUploadedFile(
                name="file.csv",
                content=content.encode("utf-8"),
                content_type="text/csv",
            )

    @pytest.mark.parametrize(
        "source_content, target_content, expected",
        [
            (
                None,
                """record_id,name,amount,date
1,John Doe,100,2023-01-15
2,Jane Smith,200,2023-01-16
4,Bob Williams,250,2023-01-18""",
                False,
            ),
            (
                """record_id,name,amount,date
1,John Doe,100,2023-01-15
2,Jane Smith,200,2023-01-16
3,Alice Johnson,150,2023-01-17""",
                None,
                False,
            ),
            (
                """record_id,name,amount,date
1,John Doe,100,2023-01-15
2,Jane Smith,200,2023-01-16
3,Alice Johnson,150,2023-01-17""",
                """record_id,name,amount,date
1,John Doe,100,2023-01-15
2,Jane Smith,200,2023-01-16
4,Bob Williams,250,2023-01-18""",
                True,
            ),
        ],
    )
    def test_valid(self, source_content, target_content, expected):
        source = self.csv_file(content=source_content)
        target = self.csv_file(content=target_content)
        serializer = ReconciliationSerializer(data={"source": source, "target": target})

        actual = serializer.is_valid()

        assert actual is expected

    @pytest.mark.parametrize(
        "source_content, target_content, expected",
        [
            (
                """record_id,name,amount,date
1,John Doe,100,2023-01-15
2,Jane Smith,200,2023-01-16
3,Alice Johnson,150,2023-01-17""",
                """record_id,name,amount,date
1,John Doe,100,2023-01-15
2,Jane Smith,200,2023-01-16
4,Bob Williams,250,2023-01-18""",
                {
                    "records_missing_in_source": [
                        {
                            "record_id": "4",
                            "name": "Bob Williams",
                            "amount": "250",
                            "date": "2023-01-18",
                        },
                    ],
                    "records_missing_in_target": [
                        {
                            "record_id": "3",
                            "name": "Alice Johnson",
                            "amount": "150",
                            "date": "2023-01-17",
                        },
                    ],
                    "discrepancies": [],
                },
            ),
        ],
    )
    def test_data(self, source_content, target_content, expected):
        source = self.csv_file(content=source_content)
        target = self.csv_file(content=target_content)
        serializer = ReconciliationSerializer(data={"source": source, "target": target})
        serializer.is_valid(raise_exception=True)

        actual = serializer.data

        assert actual == expected
