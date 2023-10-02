# Digi-Leap![Python application](https://github.com/rafelafrance/digi_leap/workflows/CI/badge.svg) [![DOI](https://zenodo.org/badge/334215090.svg)](https://zenodo.org/badge/latestdoi/334215090)

Use a neural network to find labels on a herbarium sheet

## Find Labels

[<img src="assets/show_labels.png" width="500" />](assets/show_labels.png)

We find labels with a custom trained YOLOv7 model (https://github.com/WongKinYiu/yolov7).

- Labels that the model classified as typewritten are outlined in orange
- All other identified labels are outlined in teal.

Local scripts:
- prepare_sheets.py: This formats images of herbarium sheets to prepare them for YOLO processing.
- ingest_yolo.py: This takes for output of the YOLO model and creates label images. The label name contains information about the YOLO results. The label name format:
  - `<sheet name>_<label class>_<left pixel>_<top pixel>_<right pixel>_<bottom pixel>.jpg`
  - For example: `my-herbarium-sheet_typewritten_2261_3580_3397_4611.jpg`
