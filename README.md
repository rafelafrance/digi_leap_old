# Digi-Leap![Python application](https://github.com/rafelafrance/digi_leap/workflows/CI/badge.svg)

Extract information from images of herbarium specimen label text. To do this we need to convert labels on the images into text using optical character recognition (OCR) and then extract information form the text using natural language processing (NLP). There are other steps in between to make these larger goals possible. Please note that the plan is to scale this pipeline up to more than one million herbarium sheets from various sources, ages, and with inconsistent image quality, so hand-tweaking any step in the pipeline is not feasible.

Given images like:

![Figure 1: Herbarium sample image](assets/herbarium_sample_image.jpg)

We want to:

1. [Find all the labels on the images.](#Find-Labels)
1. [OCR the cleaned up label images.](#OCR-Labels)
1. [Use NLP to extract information from the clean OCR text.](#Extract-Information)

We are going to treat this as a pipeline of Machine Learning (ML) models with swappable steps. This means that each step can be trained independently and implemented so that you can use appropriate models for any particular dataset.

## Find Labels

## OCR Labels

![Figure 2: Label with underlines](assets/label_with_underlines.jpg)

## Rebuild Labels

## Extract Information

# Run Tests

```bash
python -m unittest discover
```
