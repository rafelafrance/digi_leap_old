# Digi-Leap
This app is to help people who want to extract text information from labels on images of
museum specimens.

## There are up to 3 steps in this process:
* **find-labels**: When you have an image of a museum specimen but you have not
identified where on the sheet the labels are. We have trained a neural network to
find the labels and identify if they are typewritten or not.
* **ocr-labels**: This will extract text from a label image. It works best with
typewritten labels. OCR is notoriously fickle and we apply "tricks" to get the best
text extraction possible.
* **extract-information** (_Not implemented_).
