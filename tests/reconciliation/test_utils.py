import pytest

from credrails.apps.reconciliation.utils import CellId


class TestCellId:
    @pytest.mark.parametrize(
        "row_number, column_number, expected",
        [
            (1, 1, "A1"),
            (1, 2, "B1"),
            (3, 2, "B3"),
            (3, 26, "Z3"),
            (3, 27, "AA3"),
            (3, 52, "AZ3"),
            (3, 53, "BA3"),
            (3, 78, "BZ3"),
        ],
    )
    def test_str(self, row_number, column_number, expected):
        cell_id = CellId(row_number=row_number, column_number=column_number)

        assert str(cell_id) == expected
