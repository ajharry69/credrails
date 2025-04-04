class CellId:
    __column_numbers = {}

    def __init__(self, row_number: int, column_number: int):
        self._row_number = row_number
        self._column_number = column_number

    def __str__(self):
        return f"{self.__get_excel_column_name(column_number=self._column_number)}{self._row_number}"

    @classmethod
    def __get_excel_column_name(cls, column_number: int):
        col_num = column_number
        column = cls.__column_numbers.get(col_num, "")
        if column:
            return column

        while column_number > 0:
            column_number, remainder = divmod(column_number - 1, 26)
            column = f"{chr(65 + remainder)}{column}"
        cls.__column_numbers[col_num] = column

        return column
