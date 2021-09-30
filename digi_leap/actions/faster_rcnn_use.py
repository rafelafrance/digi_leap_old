"""Use a trained model to cut out labels on herbarium sheets."""

import torch
import torchvision
from PIL import Image
from torchvision import transforms
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.ops import batched_nms
from tqdm import tqdm

import digi_leap.pylib.box_calc as calc
import digi_leap.pylib.db as db
import digi_leap.pylib.subject as sub


def use(args):
    """Train the neural net."""
    torch.multiprocessing.set_sharing_strategy("file_system")

    state = torch.load(args.load_model)

    model = get_model()
    model.load_state_dict(state["model_state"])

    device = torch.device(args.device)
    model.to(device)

    model.eval()

    paths = db.select_sheet_paths(args.database, limit=args.limit)
    db.create_label_table(args.database, drop=True)

    label_batch = []

    for path in tqdm(paths):

        with Image.open(path) as image:
            image = image.convert("L")
            data = transforms.ToTensor()(image)

        with torch.no_grad():
            preds = model([data.to(device)])

        for pred in preds:
            boxes = pred["boxes"].detach().cpu()
            labels = pred["labels"].detach().cpu()
            scores = pred["scores"].detach().cpu()

            idx = batched_nms(boxes, scores, labels, args.nms_threshold)
            boxes = boxes[idx, :]
            labels = labels[idx]

            idx = calc.small_box_suppression(boxes, args.sbs_threshold)
            boxes = boxes[idx, :]
            labels = labels[idx]

            for i, (box, label) in enumerate(zip(boxes, labels)):
                box = box.tolist()
                label_batch.append(
                    {
                        "path": str(path),
                        "class": sub.CLASS2NAME[label.item()],
                        "offset": i,
                        "left": round(box[0]),
                        "top": round(box[1]),
                        "right": round(box[2]),
                        "bottom": round(box[3]),
                    }
                )

    db.insert_labels(args.database, label_batch)


def get_model():
    """Get the model to use."""
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(
        in_features, num_classes=len(sub.CLASSES) + 1
    )
    return model
