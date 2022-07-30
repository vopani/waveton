# import os
# import sys
from h2o_wave import Q, expando_to_dict, ui

IMAGE_TAGS = [
    {"name": "cat", "label": "Cat", "color": "$cyan"},
    {"name": "dog", "label": "Dog", "color": "$blue"}
]


IMAGES = ['https://www.kindpng.com/picc/m/183-1833650_dog-and-cat-together-hd-png-download.png']

IMAGE_ITEMS = [ui.image_annotator_item(shape=ui.image_annotator_rect(x1=649, y1=393, x2=383, y2=25), tag='cat')]#[[ui.image_annotator_item(shape=ui.image_annotator_rect(x1=64.9, y1=39.3, x2=38.3, y2=25), tag='cat')],

IMAGE_PIXEL = '300px'

# [[{'tag': 'dog', 'shape': {'rect': {'x1': 250.69, 'x2': 378.95, 'y1': 182.32, 'y2': 343.44}}}, {'tag': 'cat', 'shape': {'rect': {'x1': 129.85, 'x2': 251.75, 'y1': 201.4, 'y2': 346.62}}}]]

