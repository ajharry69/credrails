import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test.client import encode_multipart
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from credrails.apps.reconciliation.serializers import ReconciliationSerializer


class TestReconciliationViewSet:
    @staticmethod
    def csv_file(content):
        if content is not None:
            return SimpleUploadedFile(
                name="file.csv",
                content=content.encode("utf-8"),
                content_type="text/csv",
            )

    def setup_method(self):
        self.client = APIClient()

    @pytest.mark.parametrize(
        "source_content, target_content, expected_data",
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
            (
                """record_id,name,amount,date
1,JOHN DOE,100,2023-01-15
2,Jane Smith,200,16/01/2023
3,Alice Johnson,150,2023-01-17
4,Jack Jill,15.0,2023-01-17""",
                """record_id,name,amount,date
1,John Doe,100.00,2023-01-15
2,jane smith,200,2023-01-16
4,Jack Jill,150,2023-01-17
5,Bob Williams,250,2023-01-18""",
                {
                    "records_missing_in_source": [
                        {
                            "record_id": "5",
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
                    "discrepancies": [
                        {
                            "spreadsheet_cell_id": "B2",
                            "column_name": "name",
                            "row_number": 2,
                            "reason": "Mismatching case",
                        },
                        {
                            "spreadsheet_cell_id": "B3",
                            "column_name": "name",
                            "row_number": 3,
                            "reason": "Mismatching case",
                        },
                        {
                            "spreadsheet_cell_id": "D3",
                            "column_name": "date",
                            "row_number": 3,
                            "reason": "Mismatching date format",
                        },
                        {
                            "spreadsheet_cell_id": "C5",
                            "column_name": "amount",
                            "row_number": 5,
                            "reason": "Mismatching numbers",
                        },
                    ],
                },
            ),
            (
                """record_id,name,amount,date,status
1,John Doe,100,2023-01-15,active
2,Jane Smith,200,2023-01-16,inactive
3,Alice Johnson,150,2023-01-17,active""",
                """record_id,name,amount,date,status
1,John Doe,100,2023-01-15,ACTIVE
2,Jane Smith,200,2023-01-16,inactive
4,Bob Williams,250,2023-01-18,active""",
                {
                    "records_missing_in_source": [
                        {
                            "record_id": "4",
                            "name": "Bob Williams",
                            "amount": "250",
                            "date": "2023-01-18",
                            "status": "active",
                        },
                    ],
                    "records_missing_in_target": [
                        {
                            "record_id": "3",
                            "name": "Alice Johnson",
                            "amount": "150",
                            "date": "2023-01-17",
                            "status": "active",
                        },
                    ],
                    "discrepancies": [
                        {
                            "spreadsheet_cell_id": "E2",
                            "column_name": "status",
                            "row_number": 2,
                            "reason": "Mismatching case",
                        },
                    ],
                },
            ),
            (
                """record_id,name,amount,date""",
                """record_id,name,amount,date
1,John Doe,100,2023-01-15""",
                {
                    "records_missing_in_source": [
                        {
                            "record_id": "1",
                            "name": "John Doe",
                            "amount": "100",
                            "date": "2023-01-15",
                        },
                    ],
                    "records_missing_in_target": [],
                    "discrepancies": [],
                },
            ),
            (
                """record_id,name,amount,date""",
                """record_id,name,amount,date""",
                {
                    "records_missing_in_source": [],
                    "records_missing_in_target": [],
                    "discrepancies": [],
                },
            ),
        ],
    )
    def test_reconcile_post(self, source_content, target_content, expected_data):
        source = self.csv_file(content=source_content)
        target = self.csv_file(content=target_content)
        path = reverse("reconciliation:reconciliation-reconcile")
        data = {"source": source, "target": target}
        content = encode_multipart("BoUnDaRyStRiNg", data)
        content_type = "multipart/form-data; boundary=BoUnDaRyStRiNg"

        response = self.client.post(
            path=path,
            data=content,
            content_type=content_type,
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_data

    def test_reconcile_get_default(self):
        path = reverse("reconciliation:reconciliation-reconcile")

        response = self.client.get(path=path)

        assert response.status_code == status.HTTP_200_OK
        assert response.data == response.json() == {}

    def test_reconcile_get_html(self):
        path = reverse("reconciliation:reconciliation-reconcile")

        response = self.client.get(path=path, headers={"Accept": "text/html"})

        assert response.status_code == status.HTTP_200_OK
        assert response.data.keys() == {"reports", "serializer"}
        assert response.data["reports"] == {}
        assert isinstance(response.data["serializer"], ReconciliationSerializer)
        assert "Source" in response.text
        assert "Target" in response.text
        assert "Reconcile" in response.text
        assert "Reconciliation Report" in response.text
        assert "No reports. Please use the above form to retrieve reports." in response.text
