import re

import datatable as dt
from h2o_wave import ui


def prepare_query(query: str) -> str:
    """
    Prepare query in clean syntax.
    """

    query = re.sub('data', 'q.client.data', query)
    query = re.sub('df', 'q.client.data', query)
    query = re.sub('DT', 'q.client.data', query)

    return query


def create_choices_from_list(values: list) -> list[ui.Choice]:
    """
    Create choices from list of values in Wave's Choice format.
    """

    return [ui.choice(name=str(value), label=str(value)) for value in values]


def create_table_columns(data: dt.Frame) -> list[ui.TableColumn]:
    """
    Create columns of data in Wave's TableColumn format.
    """

    return [
        ui.table_column(name=str(col), label=str(col), link=False) for col in data.names
    ]


def create_table_rows(data: dt.Frame) -> list[ui.TableRow]:
    """
    Create rows of data in Wave's TableRow format.
    """

    return [
        ui.table_row(name=str(i), cells=[str(value) for value in data[i, :].to_tuples()[0]]) for i in range(data.nrows)
    ]
