from h2o_wave import Q, ui
import pandas as pd
from h2o_wave import Q, ui, copy_expando
from PIL import Image


def load_image(filename, size=None, scale=None):
    img = Image.open(filename)
    if size is not None:
        img = img.resize((size, size), Image.ANTIALIAS)
    elif scale is not None:
        img = img.resize(
            (int(img.size[0] / scale), int(img.size[1] / scale)), Image.ANTIALIAS)
    return img


def save_image(filename, data):
    img = data.clone().clamp(0, 255).numpy()
    img = img.transpose(1, 2, 0).astype("uint8")
    img = Image.fromarray(img)
    img.save(filename)

async def display_progress_bar(q: Q, doc):    
  q.page['meta'].dialog = ui.dialog(
      name = "name" if 'name' in doc else doc['name'], 
      title = "" if 'title' in doc else doc['title'], 
      items = [] if 'items' in doc else doc['items'], 
      closable = False if 'closable' in doc else doc['closable'], 
      primary = True if 'primary' in doc else doc['primary']
  )
  await q.page.save()
  await q.sleep(1)

def ui_table_from_df(df: pd.DataFrame,
                     name: str,
                     sortables: list = None,
                     filterables: list = None,
                     searchables: list = None,
                     icons: dict = None,
                     progresses: dict = None,
                     tags: dict = None,
                     min_widths: dict = None,
                     max_widths: dict = None,
                     link_col: str = None,
                     multiple: bool = False,
                     groupable: bool = False,
                     downloadable: bool = False,
                     resettable: bool = False,
                     height: str = None,
                     checkbox_visibility: str = None) -> ui.table:

    if len(df) == 0:
        table = ui.table(
            name='name',
            columns=[ui.table_column(name='-', label='-', link=False)],
            rows=[ui.table_row(name='-', cells=[str('No data found!')])])
        return table

    if not sortables:
        sortables = []
    if not filterables:
        filterables = []
    if not searchables:
        searchables = []
    if not icons:
        icons = {}
    if not progresses:
        progresses = {}
    if not tags:
        tags = {}
    if not min_widths:
        min_widths = {}
    if not max_widths:
        max_widths = {}

    cell_types = {}
    for col in icons.keys():
        cell_types[col] = ui.icon_table_cell_type(color=icons[col]['color'])
    for col in progresses.keys():
        cell_types[col] = ui.progress_table_cell_type(
            color=progresses[col]['color'])
    for col in tags.keys():
        cell_types[col] = ui.tag_table_cell_type(name="tag_" + col,
                                                 tags=tags[col]['tags'])

    columns = [
        ui.table_column(
            name=str(x),
            label=str(x),
            sortable=True if x in sortables else False,
            filterable=True if x in filterables else False,
            searchable=True if x in searchables else False,
            cell_type=cell_types[x] if x in cell_types.keys() else None,
            min_width=min_widths[x] if x in min_widths.keys() else None,
            max_width=max_widths[x] if x in max_widths.keys() else None,
            link=True if x == link_col else False,
        ) for x in df.columns.values
    ]

    table = ui.table(name=name,
                     columns=columns,
                     rows=[
                         ui.table_row(name=str(i),
                                      cells=[
                                          str(df[col].values[i])
                                          for col in df.columns.values
                                      ]) for i in range(df.shape[0])
                     ],
                     multiple=multiple,
                     groupable=groupable,
                     downloadable=downloadable,
                     resettable=resettable,
                     height=height,
                     checkbox_visibility=checkbox_visibility)

    return table


""" DAI UTILS """


def ui_choices(alist):
	return [ui.choice(name=c, label=c) for c in alist]


def get_table_from_df(df: pd.DataFrame, rows: int, name: str, size: str):
	df = df.copy().reset_index(drop=True)
	columns = [ui.table_column(name=str(x), label=str(
            x), sortable=True, searchable=False, filterable=False) for x in df.columns.values]
	rows = min(rows, df.shape[0])
	try:
		table = ui.table(
			name=name, columns=columns,
			rows=[ui.table_row(name=str(i), cells=[str(df[col].values[i])
			                   for col in df.columns.values]) for i in range(rows)],
			groupable=False,
                    downloadable=True,
                    resettable=True,
                    multiple=False,
			height=size
		)
	except:
		table = ui.table(
			name=name, columns=[ui.choice('0', '0')],
			rows=[ui.table_row(name='0', cells=[str('No data found')])]
		)
	return table


async def update_theme(q: Q):

    copy_expando(q.args, q.client)

    if q.client.theme_dark:
        q.client.icon_color = "#CDDD38"
        q.page["meta"].theme = "light"
        # q.page['header'].icon_color = q.client.icon_color

    else:
        q.client.icon_color = "#FFFFFF"
        q.page["meta"].theme = "h2o-dark"
        # q.page['header'].icon_color = q.client.icon_color

    q.page["misc"].items[2].toggle.value = q.client.theme_dark

    await q.page.save()


def set_user_arguments(q: Q, elements):
	for element in elements:
		q.user[element] = q.args[element]

