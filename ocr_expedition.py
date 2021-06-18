#!/usr/bin/env python
# coding: utf-8

# In[1]:


# import sys
# sys.path.append('../..')


# In[2]:


from collections import defaultdict
from pathlib import Path

import enchant
import numpy as np
# import pytesseract
from IPython.display import display
from ipywidgets import interact
from PIL import Image, ImageDraw, ImageFont  # , ImageOps

# import digi_leap.const as const
import digi_leap.box_calc as calc
import digi_leap.util as util
from digi_leap.ocr import ocr_label
from digi_leap.ocr_score import BBox


# In[3]:


# ROOT = Path('..') / '..'
ROOT = Path('.')

DATA_DIR = ROOT / 'data'

LABELS_DIR = DATA_DIR / 'labels-1' / 'typewritten'
# LABELS_DIR = DATA_DIR / 'labels-1' / 'handwritten'

FONTS_DIR = ROOT / 'fonts' / 'print' / 'Source_Code_Pro'
FONT = FONTS_DIR / 'SourceCodePro-Regular.ttf'

PREVIOUS = ROOT / 'output' / 'ocr_sample_2021-05-10a'
OUTPUT = ROOT / 'output' / 'ocr_sample_2021-05-10b'


# In[4]:


LANG = 'en_US'
EXTRA_VOCAB = DATA_DIR / 'custom_vocab.txt'
VOCAB = enchant.DictWithPWL(LANG, str(EXTRA_VOCAB))


# In[5]:


NAMES = {p.name for p in PREVIOUS.glob('*.jpg')}
IMAGES = [p for p in LABELS_DIR.glob('*.jpg') if p.name in NAMES]


# In[6]:


class FontDict(dict):
    def __missing__(self, key):
        return ImageFont.truetype(str(FONT), key)


# In[7]:


base = 48
fonts = FontDict()
base_font = ImageFont.truetype(str(FONT), base)

scaled_by = 'scaled by: '


# In[10]:


def show_image(idx):
    path = IMAGES[idx]
    print(path)
    label = Image.open(path)
    display(label)


interact(show_image, idx=(0, len(IMAGES) - 1));


# In[8]:


def show_ocr(idx):
    path = IMAGES[idx]
    print(path)
    label = Image.open(path)
    width, height = label.size

    image = Image.new('RGB', (width, height * 2))
    image.paste(label, (0, 0))

    result = Image.new('RGB', label.size, color='white')

    score = ocr_label(path)
    scale = [m for m in score.score.method if m.startswith(scaled_by)]
    scale = float(scale[0].removeprefix(scaled_by)) if scale else 1.0

    draw = ImageDraw.Draw(result)

    for bbox in score.score.data:
        text = bbox['text']

        bl, bt, br, bb = bbox['left'], bbox['top'], bbox['right'], bbox['bottom']
        bl, bt, br, bb = bl // scale, bt // scale, br // scale, bb // scale

        for size in range(base, 8, -1):
            tl, tt, tr, tb = draw.textbbox(
                (bl, bt), text, font=fonts[size], anchor='lt')
            if br >= tr and bb >= tb:
                break
        else:
            continue

        draw.rectangle((bl, bt, br, bb), outline='red')
        draw.rectangle((tl, tt, tr, tb), outline='blue')
        draw.text((bl, bt), text, font=fonts[size], fill='black', anchor='lt')

    image.paste(result, (0, height))

    display(image)


# show_ocr(3)
# interact(show_ocr, idx=(0, len(IMAGES) - 1));


# In[8]:


class MergedBox(BBox):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.boxes: list[BBox] = []


# In[9]:


def init_boxes(old_boxes, image_width, *, scale=1.0, pad_chars=2):
    """Pad the bounding boxes on the left & right."""
    boxes = []

    for box in old_boxes:
        ll, tt, rr, bb = box.left, box.top, box.right, box.bottom
        ll, tt, rr, bb = ll // scale, tt // scale, rr // scale, bb // scale

        per_char = (rr - ll) / len(box.text)
        ll = max(0, ll - pad_chars * per_char)
        rr = min(image_width, rr + pad_chars * per_char)

        new_box = MergedBox(left=ll, top=tt, right=rr, bottom=bb, text=box.text)
        new_box.boxes.append(box)
        boxes.append(new_box)

    return boxes


# In[10]:


def link_box(inters, row, chains, chain):
    linked = np.argwhere(inters[row] > 0.0).squeeze(1)
    for r in linked:
        if chains[r] == 0:
            chains[r] = chain
            link_box(inters, r, chains, chain)


# In[11]:


def merge_boxes(boxes, threshold=0.1):
    """Merge left/right extended boxes that overlap."""
    array = np.array([b.as_list() for b in boxes])
    inters = calc.all_fractions(array)
    inters = np.triu(inters)

    mask = np.where(inters < threshold)
    inters[mask] = 0.0

    chain = 0
    chains = defaultdict(int)
    for r, row in enumerate(inters):
        if chains[r] != 0:
            continue
        chain += 1
        link_box(inters, r, chains, chain)

    merged = defaultdict(lambda: MergedBox())
    for b, chain in chains.items():
        box = boxes[b]
        group = merged[chain]
        group.boxes.append(box)
        group.left = min(group.left, box.left)
        group.top = min(group.top, box.top)
        group.right = max(group.right, box.right)
        group.bottom = max(group.bottom, box.bottom)

    for group in merged.values():
        group.boxes = sorted(group.boxes, key=lambda b: (b.left, b.top))
        group.text = ' '.join(b.text for b in group.boxes)

    return list(merged.values())


# In[14]:


def merge_cells(idx):
    path = IMAGES[idx]
    print(path)
    label = Image.open(path)
    width, height = label.size

    image = Image.new('RGB', (width, height * 2))
    image.paste(label, (0, 0))

    result = Image.new('RGB', label.size, color='white')

    score = ocr_label(path)
    print(score.score)
    print(score.score.text)

    scale = [m for m in score.score.method if m.startswith(scaled_by)]
    scale = float(scale[0].removeprefix(scaled_by)) if scale else 1.0

    boxes0 = init_boxes(score.score.data, width, scale=scale)
    boxes = boxes0
    boxes = merge_boxes(boxes, threshold=0.1)

    draw = ImageDraw.Draw(result)

    for b in boxes:
        for size in range(base, int(16 / scale), -1):
            c = draw.textbbox((b.left, b.top), b.text, font=fonts[size], anchor='lt')
            if b.right >= c[2] and b.bottom >= c[3]:
                break
            else:
                continue

#         draw.rectangle(b.as_list(), outline='red')
#         # draw.rectangle(c.as_list(), outline='blue')
        draw.text((b.left, b.top), b.text, font=fonts[size], fill='black', anchor='lt')

#     for b in boxes0:
#         draw.rectangle(b.as_list(), outline='blue')

    image.paste(util.to_pil(score.image), (0, height))
#     image.paste(result, (0, height))
    display(image)


# merge_cells(46)
# merge_cells(48)
interact(merge_cells, idx=(0, len(IMAGES) - 1));


# In[ ]:




