"""Generate training data."""

import csv
import json

import torch
from PIL import Image
from torch.utils.data import Dataset

import digi_leap.detection.transforms as T
from digi_leap.subject import SubjectTrainData


class FasterRcnnData(Dataset):
    """Generate augmented training data."""

    reconcile = {
        '': '',
        'Barcode': 'Barcode',
        'Barcode_Both': 'Barcode',
        'Barcode_Both_Handwritten': 'Barcode',
        'Barcode_Both_Handwritten_Typewritten': 'Barcode',
        'Barcode_Both_Typewritten': 'Barcode',
        'Barcode_Handwritten': 'Barcode',
        'Barcode_Handwritten_Typewritten': 'Barcode',
        'Barcode_Typewritten': 'Barcode',
        'Both': 'Both',
        'Both_Handwritten': 'Both',
        'Both_Handwritten_Typewritten': 'Both',
        'Both_Typewritten': 'Both',
        'Handwritten': 'Handwritten',
        'Handwritten_Typewritten': 'Both',
        'Typewritten': 'Typewritten',
    }
    classes = len(set(reconcile.values()))

    def __init__(self, csv_file, image_dir, train):
        self.subjects = [self.subject_data(r, image_dir)
                         for r in self.read_subjects(csv_file)]
        self.transforms = self.get_transforms(train)

    def __len__(self):
        return len(self.subjects)

    def __getitem__(self, idx):
        subject = self.subjects[idx]

        boxes = subject.boxes
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])

        target = {
            'boxes': boxes,
            'labels': subject.labels,
            'image_id': torch.tensor([idx]),
            'area': area,
            'iscrowd': torch.zeros((1,), dtype=torch.int64),
        }

        image = Image.open(subject.path)

        if self.transforms is not None:
            image, target = self.transforms(image, target)

        return image, target

    def subject_data(self, row, image_dir):
        """Create a subject row record."""
        path = image_dir / row['subject_file_name']

        boxes = []
        for box in [v for k, v in row.items() if k.startswith('merged_box_') and v]:
            box = json.loads(box)
            boxes.append([int(v) for v in box.values()])

        labels = []
        for type_ in [v for k, v in row.items() if k.startswith('merged_type_') and v]:
            labels.append(self.reconcile[type_])

        return SubjectTrainData(path=path, boxes=boxes, labels=labels)

    @staticmethod
    def read_subjects(csv_file):
        """Read the subjects from a reconciled CSV file."""
        with open(csv_file) as in_file:
            reader = csv.DictReader(in_file)
            subjects = [s for s in reader]
        return subjects

    @staticmethod
    def get_transforms(train):
        """Build transforms based on the type of dataset."""
        transforms = [T.ToTensor()]
        if train:
            transforms.append(T.RandomHorizontalFlip(0.25))
            transforms.append(T.RandomVerticalFlip(0.25))
            transforms.append(T.RandomIoUCrop())
            transforms.append(T.RandomZoomOut())
            transforms.append(T.RandomPhotometricDistort())
        return T.Compose(transforms)
