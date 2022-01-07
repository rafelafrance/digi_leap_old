"""Use a trained model to cut out labels on herbarium sheets."""
import torch
import torchvision
from PIL import Image
from torchvision import transforms
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.ops import batched_nms
from tqdm import tqdm

from . import box_calc as calc
from . import db
from . import subject as sub


def find_labels(args):
    """Train the neural net."""
    state = torch.load(args.load_model)

    model = get_model()
    model.load_state_dict(state["model_state"])

    device = torch.device(args.device)
    model.to(device)

    model.eval()

    db.create_label_table(args.database, drop=True)
    sheets = db.select_sheets(args.database, limit=args.limit)

    label_batch = []

    for sheet in tqdm(sheets):

        with Image.open(sheet["path"]) as image:
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
                        "sheet_id": sheet["sheet_id"],
                        "label_run": args.label_run,
                        "offset": i,
                        "class": sub.CLASS2NAME[label.item()],
                        "label_left": round(box[0]),
                        "label_top": round(box[1]),
                        "label_right": round(box[2]),
                        "label_bottom": round(box[3]),
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
