#!/usr/bin/env python
# coding: utf-8

# # Convert reconciled bounding boxes into YOLO training data

# ## Setup

# In[1]:


import csv
import json
from os import makedirs
from pathlib import Path
from shutil import rmtree

import numpy as np
import pandas as pd
from PIL import Image, ImageDraw
from sklearn.model_selection import train_test_split
from tqdm import tqdm

from digi_leap.subject import Subject, RECONCILE_TYPES


# ## Data that may change for each user or run

# In[2]:


DATA_DIR = Path.cwd() / "data"

LABEL_BABEL_2_DIR = DATA_DIR / "label-babel-2"
SHEETS_2_DIR = LABEL_BABEL_2_DIR / "herbarium-sheets-small"

RECONCILED = LABEL_BABEL_2_DIR / "17633_label_babel_2.reconciled.csv"
TRAIN_CSV = LABEL_BABEL_2_DIR / "17633_label_babel_2.train.csv"
TEST_CSV = LABEL_BABEL_2_DIR / "17633_label_babel_2.test.csv"

YOLO_TRAIN_CSV = LABEL_BABEL_2_DIR / "17633_label_babel_2.yolo.train.csv"
YOLO_VAL_CSV = LABEL_BABEL_2_DIR / "17633_label_babel_2.yolo.val.csv"

YOLO_DIR = LABEL_BABEL_2_DIR / "yolo"

IMAGE_TRAIN_DIR = YOLO_DIR / "images" / "train"
IMAGE_TEST_DIR = YOLO_DIR / "images" / "test"
IMAGE_VAL_DIR = YOLO_DIR / "images" / "val"

LABEL_TRAIN_DIR = YOLO_DIR / "labels" / "train"
LABEL_TEST_DIR = YOLO_DIR / "labels" / "test"
LABEL_VAL_DIR = YOLO_DIR / "labels" / "val"


# In[3]:


SEED = 4484


# Resize images to this width and height

# In[5]:


IMAGE_SIZE = 640


# How much of the training data goes towards validation

# In[6]:


VAL_SPLIT = 0.25


# Keep prints of numpy arrays reasonably pretty.

# In[7]:


np.set_printoptions(precision=6)


# ## Create directories

# In[8]:


rmtree(IMAGE_TRAIN_DIR, ignore_errors=True)
rmtree(IMAGE_TEST_DIR, ignore_errors=True)
rmtree(IMAGE_VAL_DIR, ignore_errors=True)

rmtree(LABEL_TRAIN_DIR, ignore_errors=True)
rmtree(LABEL_TEST_DIR, ignore_errors=True)
rmtree(LABEL_VAL_DIR, ignore_errors=True)


# In[9]:


makedirs(IMAGE_TRAIN_DIR, exist_ok=True)
makedirs(IMAGE_TEST_DIR, exist_ok=True)
makedirs(IMAGE_VAL_DIR, exist_ok=True)

makedirs(LABEL_TRAIN_DIR, exist_ok=True)
makedirs(LABEL_TEST_DIR, exist_ok=True)
makedirs(LABEL_VAL_DIR, exist_ok=True)


# ## Read the reconciled training, validation, and testing data

# In[11]:


with open(TRAIN_CSV) as csv_file:
    reader = csv.DictReader(csv_file)
    train_subjects = [r for r in reader]

with open(TEST_CSV) as csv_file:
    reader = csv.DictReader(csv_file)
    test_rows = [r for r in reader]


# ### Split into training and validation data sets

# In[12]:


train_rows, val_rows = train_test_split(
    train_subjects, test_size=VAL_SPLIT, shuffle=True, random_state=SEED
)


# ## Write resized images to training and validation directories

# In[28]:


def write_resized(row, image_dir):
    size = json.loads(row["image_size"])
    row["image_size"] = [size["width"], size["height"]]
    row["resized"] = [IMAGE_SIZE, IMAGE_SIZE]

    src = SHEETS_2_DIR / row["image_file"]
    dst = image_dir / row["image_file"]
    image = Image.open(src)
    image = image.resize((IMAGE_SIZE, IMAGE_SIZE))
    image.save(dst)


# In[16]:


for row in tqdm(train_rows):
    write_resized(row, IMAGE_TRAIN_DIR)

for row in tqdm(val_rows):
    write_resized(row, IMAGE_VAL_DIR)

for row in tqdm(test_rows):
    write_resized(row, IMAGE_TEST_DIR)


# ## Create machine learning labels from herbarium label types

# In[ ]:


def create_labels(row):
    types = [v for k, v in row.items() if k.startswith("merged_type_")]
    for i, label in enumerate(types, 1):
        row[f"label_{i}"] = RECONCILE_TYPES[label.strip("_")]


# In[18]:


for row in tqdm(train_rows):
    create_labels(row)

for row in tqdm(val_rows):
    create_labels(row)

for row in tqdm(test_rows):
    create_labels(row)


# ## Resize bounding boxes

# In[19]:


def resize_boxes(row):
    width, height = row["image_size"]

    boxes = [v for k, v in row.items() if k.startswith("merged_box_") and v]
    boxes = np.array(
        [Subject.bbox_from_json(b, (width, height)) for b in boxes], dtype=np.float32
    )

    if len(boxes) == 0:
        return

    boxes[:, [0, 2]] *= row["resized"][0] / width
    boxes[:, [1, 3]] *= row["resized"][1] / height
    boxes = np.floor(boxes)

    for i, box in enumerate(boxes, 1):
        row[f"resized_{i}"] = box


# In[21]:


for row in tqdm(train_rows):
    resize_boxes(row)

for row in tqdm(val_rows):
    resize_boxes(row)

for row in tqdm(test_rows):
    resize_boxes(row)


# ## Convert resized bounding boxes for a subject into YOLO format

# In[22]:


def to_yolo(row):
    width, height = row["resized"]

    boxes = [v for k, v in row.items() if k.startswith("resized_") and len(v)]
    boxes = np.array(boxes, dtype=np.float32)

    if len(boxes) == 0:
        return []

    center_x = (boxes[:, 0] + boxes[:, 2]) / 2.0
    center_y = (boxes[:, 1] + boxes[:, 3]) / 2.0
    wide = boxes[:, 2] - boxes[:, 0] + 1
    high = boxes[:, 3] - boxes[:, 1] + 1
    boxes = np.vstack((center_x, center_y, wide, high)).transpose()
    boxes[:, [0, 2]] /= width
    boxes[:, [1, 3]] /= height

    for i, box in enumerate(boxes, 1):
        row[f"yolo_{i}"] = box

    return boxes


# In[23]:


for row in tqdm(train_rows):
    to_yolo(row)

for row in tqdm(val_rows):
    to_yolo(row)

for row in tqdm(test_rows):
    to_yolo(row)


# ## Save the reworked training and validation CSVs

# In[24]:


df = pd.DataFrame(train_rows)
df.to_csv(YOLO_TRAIN_CSV, index=False)

df = pd.DataFrame(val_rows)
df.to_csv(YOLO_VAL_CSV, index=False)


# ## Write YOLO bounding boxes to training, validation, and test files

# In[25]:


def write_yolo(row, label_dir):
    path = Path(row["image_file"]).stem
    path = label_dir / f"{path}.txt"

    boxes = to_yolo(row)
    labels = [v for k, v in row.items() if k.startswith("label_")]

    if len(boxes) == 0:
        return

    with open(path, "w") as out_file:
        for label, box in zip(labels, boxes):
            bbox = np.array2string(box, formatter={"float_kind": lambda x: "%.6f" % x})
            out_file.write(f"{label} {bbox[1:-1]}\n")


# In[26]:


for row in tqdm(train_rows):
    write_yolo(row, LABEL_TRAIN_DIR)

for row in tqdm(val_rows):
    write_yolo(row, LABEL_VAL_DIR)

for row in tqdm(test_rows):
    write_yolo(row, LABEL_TEST_DIR)


# # Simple tests on the conversion to YOLO

# ## Show resized bounding boxes

# In[21]:


def show_resized(idx):
    row = train_rows[idx]

    image = Image.open(IMAGE_TRAIN_DIR / row["image_file"])
    draw = ImageDraw.Draw(image)

    boxes = [v for k, v in row.items() if k.startswith("resized_")]
    for box in boxes:
        draw.rectangle(box, outline="red", width=2)

    # display(image)


# show_resized(0)


# ## Show YOLO bounding boxes

# In[22]:


def show_yolo(idx):
    row = train_rows[idx]

    width, height = row["image_size"]

    image = Image.open(SHEETS_2_DIR / row["image_file"])
    draw = ImageDraw.Draw(image)

    boxes = [v for k, v in row.items() if k.startswith("merged_box_") and len(v)]
    boxes = np.array(
        [Subject.bbox_from_json(b, (width, height)) for b in boxes], dtype=np.float32
    )
    for box in boxes:
        draw.rectangle(box, outline="blue", width=4)

    labels, boxes = to_yolo(row)

    for box in boxes:
        radius_x = (box[2] * width - 1) / 2
        radius_y = (box[3] * height - 1) / 2
        x0 = int(box[0] * width - radius_x)
        y0 = int(box[1] * height - radius_y)
        x1 = int(box[0] * width + radius_x)
        y1 = int(box[1] * height + radius_y)
        draw.rectangle((x0, y0, x1, y1), outline="red", width=2)

    # display(image)


# show_yolo(0)


# In[ ]:
