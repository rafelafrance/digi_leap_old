# Digi-Leap![Python application](https://github.com/rafelafrance/digi_leap/workflows/CI/badge.svg)

Use a neural network to find labels on a herbarium sheet

## Find Labels

[<img src="assets/show_labels.png" width="500" />](assets/show_labels.png)

We find labels with a custom trained YOLOv7 model (https://github.com/WongKinYiu/yolov7).

- Labels that the model classified as typewritten are outlined in orange
- All other identified labels are outlined in teal.

Local scripts:
- `build_training_data.py`: This formats images of herbarium sheets to prepare them for training a YOLO model.
  - This script also requires a CSV file containing the paths to the herbarium sheets and the class and location of the labels on that sheet.
- `build_inference_data.py`: This formats herbarium sheet images for YOLO inference.
  - It requires a CSV file containing the paths to all of the herbarium sheets.
- `results_to_labels.py`: This takes for output of the YOLO model and creates label images. The label name contains information about the YOLO results. The label name format:
  - `<sheet name>_<label class>_<left pixel>_<top pixel>_<right pixel>_<bottom pixel>.jpg`
  - For example: `my-herbarium-sheet_typewritten_2261_3580_3397_4611.jpg`
- `filter_labels.py`: Move typewritten label images into a separate directory.
- `fix_file_names.py`: I had a problem where herbarium sheet file names were given as URLs and it confused the Pillow (PIL) module so I renamed the files to remove problem characters. You probably won't need this.
- `old_*.py`: These modules are for ingesting training data from Zooniverse "expeditions". They are old and need to be rewritten.

You will notice that there are no scripts for running the YOLO models directly. You will need to download that repository separately and run its scripts. Example invocations of YOLO scripts are below:

```bash
python train.py \
--weights yolov7.pt \
--data data/custom.yaml \
--workers 4 \
--batch-size 4 \
--cfg cfg/training/yolov7.yaml \
--name yolov7 \
--hyp data/hyp.scratch.p5.yaml \
--epochs 100 \
--exist-ok
```

```bash
python detect.py \
--weights runs/train/yolov7_e100/weights/best.pt \
--source inference-640/ \
--save-txt \
--save-conf \
--project runs/inference-640/yolov7_e100/ \
--exist-ok \
--nosave \
--name rom2_2022-10-03 \
--conf-thres 0.1
```
