"""Common runner functions."""
import torch

# def collate_fn(batch):
#     """Fix the batch parameters."""
#     return tuple(zip(*batch))


def collate_fn(batch):
    """Fix the batch parameters."""
    images, targets, image_ids = tuple(zip(*batch))
    images = torch.stack(images)
    images = images.float()

    boxes = [t["bboxes"].float() for t in targets]
    labels = [t["labels"].float() for t in targets]
    img_size = torch.tensor([t["img_size"] for t in targets]).float()
    img_scale = torch.tensor([t["img_scale"] for t in targets]).float()

    annotations = {
        "bbox": boxes,
        "cls": labels,
        "img_size": img_size,
        "img_scale": img_scale,
    }

    return images, annotations, targets, image_ids
