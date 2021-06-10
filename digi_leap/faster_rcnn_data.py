"""Generate training data."""

import csv
import json

import torch
from PIL import Image
from torch.utils.data import Dataset

import digi_leap.detection.transforms as T
from digi_leap.subject import RECONCILE_TYPES, SubjectTrainData


class FasterRcnnData(Dataset):
    """Generate augmented training data."""

    def __init__(self, subjects, train, size=(600, 400)):
        self.subjects = subjects
        self.size = size
        self.transforms = self.get_transforms(train)

    def __len__(self):
        return len(self.subjects)

    def __getitem__(self, idx):
        subject = self.subjects[idx]
        image = Image.open(subject.path)

        boxes = torch.as_tensor(subject.boxes, dtype=torch.float32)
        # boxes = boxes.squeeze(0)
        area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])

        target = {
            'boxes': boxes,
            'labels': torch.as_tensor(subject.labels, dtype=torch.int64),
            'image_id': torch.as_tensor(subject.id, dtype=torch.int64),
            'area': area,
            'iscrowd': torch.zeros((len(subject.labels),), dtype=torch.int64),
        }

        if self.transforms is not None:
            image, target = self.transforms(image, target)

        return image, target

    def normalize_image(self, image, subject):
        """Make images the same size."""

    @classmethod
    def read_subjects(cls, csv_file, image_dir):
        """Read the subjects from a reconciled CSV file."""
        with open(csv_file) as in_file:
            reader = csv.DictReader(in_file)
            subjects = [s for s in reader]
        subjects = [s for r in subjects if (s := cls.subject_data(r, image_dir))]
        return subjects

    @staticmethod
    def subject_data(row, image_dir):
        """Create a subject row record."""
        path = image_dir / row['subject_file_name']
        id_ = int(row['subject_id'])

        boxes = []
        for box in [v for k, v in row.items() if k.startswith('merged_box_') and v]:
            box = json.loads(box)
            boxes.append([int(v) for v in box.values()])

        labels = []
        for type_ in [v for k, v in row.items() if k.startswith('merged_type_') and v]:
            type_ = type_.strip('_')
            labels.append(RECONCILE_TYPES[type_])

        if not boxes or not labels:
            print(path)
            return None

        return SubjectTrainData(id=id_, path=path, boxes=boxes, labels=labels)

    def get_transforms(self, train):
        """Build transforms based on the type of dataset."""
        transforms = [T.ToTensor(), T.Resize(self.size)]
        if train:
            transforms.append(T.RandomHorizontalFlip())
            transforms.append(T.RandomVerticalFlip())
            transforms.append(T.ColorJitter())
        return T.Compose(transforms)
