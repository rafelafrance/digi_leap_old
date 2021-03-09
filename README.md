# Digi-Leap
Extract information from images of herbarium specimens. 

The scripts are in this directory, and the notebooks/ directory contain code that I used to explore strategies for doing the various scripts. I.e. the scripts are the real code and the notebooks are old code.

Given an image like:

![Herbarium Sample Image](assets/herbarium_sample_image.jpg)

We want to:
1. [Find all the labels on the image.](#Find-Labels)
1. [Crop and clean up the labels so that we can OCR them.](#Clean-Labels)
1. [OCR the cleaned up label images.](#OCR-Labels)
1. [Cleanup the OCR text.](#Clean-OCR-Text)
1. [Use NLP to extract information from the clean OCR text.](#Extract-Information)

We are going to treat this as a pipeline of Machine Learning (ML) models with swappable steps. This means that each step may be independently trained and implemented so that appropriate models may be used for any particular dataset.

## Find Labels

## Clean Labels

## OCR Labels

## Clean OCR Text

## Extract Information
