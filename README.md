# Digi-Leap![Python application](https://github.com/rafelafrance/digi_leap/workflows/CI/badge.svg) [![DOI](https://zenodo.org/badge/334215090.svg)](https://zenodo.org/badge/latestdoi/334215090)

This repository combines all of the following repositories using `git subtree`:
- [finder](https://github.com/rafelafrance/digi_leap/tree/main/finder/README.md) Use a neural net to find labels on herbarium sheets. [Repository](https://github.com/rafelafrance/label_finder)
- [ensemble](https://github.com/rafelafrance/digi_leap/tree/main/ensemble/README.md) Use an ensemble of image processing and OCR engines to extract text from herbarium labels. [Repository](https://github.com/rafelafrance/ocr_ensemble)
- [flora](https://github.com/rafelafrance/digi_leap/tree/main/flora/README.md) Use FloraTraiter to extract Darwin Core terms and data from herbarium label text. [Repository](https://github.com/rafelafrance/FloraTraiter)
- [llm](https://github.com/rafelafrance/digi_leap/tree/main/llm/README.md) Use ChatGPT4 to extract Darwin Core terms and data from herbarium label text. [Repository](https://github.com/rafelafrance/traiter_llm)
- [reconcile](https://github.com/rafelafrance/digi_leap/tree/main/reconcile/README.md) Reconcile extracted Darwin Core data gotten from ChatGPT4 and FloraTraiter. [Repository](https://github.com/rafelafrance/reconcile_traits)
- [server](https://github.com/rafelafrance/digi_leap/tree/main/server/README.md) A simple web server to demonstrate Digi-Leap functionality. [Repository](https://github.com/rafelafrance/digi_leap_server)

You can download and run each of the above subtrees on their own. This repository is only recommended if you want to run the entire Digi-Leap pipeline. For example, if you only want to parse traits using the FloraTraiter rule-based parser you can download & use https://github.com/rafelafrance/FloraTraiter on its own.

## Reference

See the following publication in _Applications in Plant Sciences_:

_Humans in the Loop: Community science and machine learning
synergies for overcoming herbarium digitization bottlenecks_

Robert Guralnick, Raphael LaFrance, Michael Denslow, Samantha Blickhan, Mark
Bouslog, Sean Miller, Jenn Yost, Jason Best, Deborah L Paul, Elizabeth Ellwood,
Edward Gilbert, Julie Allen

## Pipeline outline

Extract information from images of herbarium specimen label sheets. This is the automated portion of a full solution that includes humans-in-the-loop.

Given images like:

[<img src="assets/sheet.jpg" width="500" />](assets/sheet.jpg)

We want to:

1. [Find all the labels on the images.](#Find-Labels)
2. [OCR the cleaned up label images.](#OCR-Labels)
3. [Use Traiter to extract information from the clean OCR text.](#Rule-based-trait-extraction)
4. [Use a large language model (LLM) to get traits from OCR text.](#Large-language-model-trait-extraction)
5. [Reconcile trait output from the Traiter and the LLM.](#Reconcile-traits)

There are many moving parts to this project and I have broken this project into several repositories, use another external repository (for YOLO7) and possibly use an external server (for GPT4).

### Find Labels

[<img src="assets/show_labels.png" width="500" />](assets/show_labels.png)

We find labels with a custom trained YOLOv7 model (https://github.com/WongKinYiu/yolov7).

- Labels that the model classified as typewritten are outlined in orange.
- All other identified labels are outlined in teal.

### OCR Labels

[<img src="assets/show_ocr_text.png" width="500" />](assets/show_ocr_text.png)

We use an ensemble of image processing techniques combined with different OCR engines to get the raw data used to build the final text output. Currently, we are using 4 image processing techniques and 2 OCR engines.

Image processing techniques:

1. Do nothing to the image. This works best with clean new herbarium sheets.
2. We slightly blur the image, scale it to a size that works with many OCR images, orient the image to get it rightside up, and then deskew the image to finetune its orientation.
3. We perform all the steps in #2 and additionally perform a Sauvola (Sauvola & Pietikainen, 2000) binarization of the image, which often helps improve OCR results.
4. We do all the steps in #3, then remove “snow” (image speckles) and fill in any small “holes” in the binarized image.

OCR engines:

1. Tesseract OCR (Smith 2007).
2. EasyOCR (https://github.com/JaidedAI/EasyOCR).

Therefore, there are 8 possible combinations of image processing and OCR engines. We found, by scoring against a gold standard, that using all 8 combinations does not always yield the best results. Currently, we use 6/8 combinations with binarize/EasyOCR and denoise/EasyOCR deemed unhelpful.

After the image processing & OCR combinations we then:

1. Perform minor edits to fix some common OCR errors like the addition of spaces before punctuation or common character substitutions.
2. Next we find the Levenshtein distance for all pairs of text sequences and remove any sequence that has a Levenshtein score greater than a predetermined cutoff (128) from the best Levenshtein score.
3. The next step in the workflow is to use a Multiple Sequence Alignment (MSA) algorithm that is directly analogous to the ones used for biological sequences but instead of using a PAM or BLOSUM substitution matrix we use a visual similarity matrix. Exact visual similarity depends on the font so an exact distance is not feasible. Instead we use a rough similarity score that ranges from +2, for characters that are identical, to -2, where the characters are wildly different like a period and a W. We also used a gap penalty of -3 and a gap extension penalty of -0.5.
4. Finally, we edit the MSA consensus sequence with a spell checker, add or remove spaces within words, and fix common character substitutions.

### Rule based trait extraction

We are currently using a hierarchy of spaCy (https://spacy.io/) rule-based parsers to extract information from the labels. One level of parsers finds anchor words, another level of parsers finds common phrases around the anchor words, etc. until we have a final set of Darwin Core terms from that label.

#### Parsing strategy

1. Have experts identify relevant terms and target traits.
2. We use expert identified terms to label terms using spaCy's phrase matchers. These are sometimes traits themselves but are more often used as anchors for more complex patterns of traits.
3. We then build up more complex terms from simpler terms using spaCy's rule-based matchers repeatedly until there is a recognizable trait. See the image below.
4. We may then link traits to each other (entity relationships) using spaCy's dependency matchers.
   1. Typically, a trait gets linked to a higher level entity like SPECIES <--- FLOWER <--- {COLOR, SIZE, etc.} and not peer to peer like PERSON <---> ORG.

#### Large language model trait extraction

### Reconcile traits

## Run Tests

```bash
cd /to/digi_leap/directory
python -m unittest discover
```
