# Digi-Leap![Python application](https://github.com/rafelafrance/digi_leap/workflows/CI/badge.svg)

[![DOI](https://zenodo.org/badge/334215090.svg)](https://zenodo.org/badge/latestdoi/334215090)



Extract information from images of herbarium specimen label sheets. This is the automated portion of a full solution that includes humans-in-the-loop.

Given images like:

[<img src="static/sheets/86b6d226-5498-40aa-a165-7b2f902090a3.jpg" width="500" />](static/sheets/86b6d226-5498-40aa-a165-7b2f902090a3.jpg)

We want to:

1. [Find all the labels on the images.](#Find-Labels)
2. [OCR the cleaned up label images.](#OCR-Labels)
3. [Use NLP to extract information from the clean OCR text.](#Extract-Information)

## Find Labels

[<img src="assets/show_labels.png" width="500" />](assets/show_labels.png)

This is using a custom trained YOLOv7 model (https://github.com/WongKinYiu/yolov7).

- Labels that the model classified as typewritten are outlined in orange
- All other identified labels are outlined in teal.

## OCR Labels

[<img src="assets/show_ocr_text.png" width="500" />](assets/show_ocr_text.png)

This is using an ensemble of image processing techniques combined with different OCR engines to get the raw data used to build the final text output. Currently, we are using 4 image processing techniques and 2 OCR engines.

Image processing techniques:

1. Do nothing to the image. This works best with clean new herbarium sheets.
2. We slightly blur the image, scale it to a size that works with many OCR images, orient the image to get it rightside up, and then deskew the image to finetune its orientation.
3. We perform all of the steps in #2 and additionally perform a Sauvola (Sauvola & Pietikainen, 2000) binarization of the image, which often helps improve OCR results.
4. We do all of the steps in #3, then remove “snow” (image speckles) and fill in any small “holes” in the binarized image.

OCR engines:

1. Tesseract OCR (Smith 2007).
2. EasyOCR (https://github.com/JaidedAI/EasyOCR).

 Therefore, there are 8 possible combinations of image processing and OCR engines. We found, by scoring against a gold standard, that using all 8 combinations does not always yield the best results. Currently, we use 6/8 combinations with binarize/EasyOCR and denoise/EasyOCR deemed unhelpful.

After the image processing & OCR combinations we then:

1. Perform minor edits to fix some common OCR errors like the addition of spaces before punctuation or common character substitutions.
2. Next we find the Levenshtein distance for all pairs of text sequences and remove any sequence that has a Levenshtein score greater than a predetermined cutoff (128) from the best Levenshtein score.
3. The next step in the workflow is to use a Multiple Sequence Alignment (MSA) algorithm that is directly analogous to the ones used for biological sequences but instead of using a PAM or BLOSUM substitution matrix we use a visual similarity matrix. Exact visual similarity depends on the font so an exact distance is not feasible. Instead we use a rough similarity score that ranges from +2, for characters that are identical, to -2, where the characters are wildly different like a period and a W. We also used a gap penalty of -3 and a gap extension penalty of -0.5.
4. Finally, we edit the MSA consensus sequence with a spell checker, add or remove spaces within words, and fix common character substitutions.

## Extract Information

**This step is not complete.**

We are currently using a hierarchy of spaCy (https://spacy.io/) rule-based parsers to extract information from the labels. One level of parsers finds anchor words, another level of parsers finds common phrases around the anchor words, etc. until we have a final set of Darwin Core terms from that label.

# Run Tests

```bash
python -m unittest discover
```
