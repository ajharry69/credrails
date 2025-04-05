from django import template

register = template.Library()


@register.filter
def label(key):
    return {
        "records_missing_in_source": "Records Missing in Source",
        "records_missing_in_target": "Records Missing in Target",
        "discrepancies": "Discrepancies",
        "spreadsheet_cell_id": "Spreadsheet Cell ID",
        "column_name": "Column Name",
        "row_number": "Row NO.",
        "reason": "Reason",
    }.get(key, key)


@register.filter
def value(_dict, key):
    return _dict[key]
