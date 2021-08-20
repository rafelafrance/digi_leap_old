# Digi-Leap![Python application](https://github.com/rafelafrance/digi_leap/workflows/CI/badge.svg)
Extract information from images of herbarium specimen labels. To do this we need to convert labels on the images into text using optical character recognition (OCR) and then extract information form the text using natural language processing (NLP). There are other steps in between to make these larger goals possible.

Given an image like:

![Figure 1: Herbarium sample image](assets/herbarium_sample_image.jpg)

We want to:
1. [Find all the labels on the image.](#Find-Labels)
   1. [Cutout and clean up the labels so that we can OCR them.](#Clean-Labels)
1. [OCR the cleaned up label images.](#OCR-Labels)
   1. [Cleanup the OCR text so that we can run NLP on it.](#Clean-OCR-Text)
1. [Use NLP to extract information from the clean OCR text.](#Extract-Information)
1. [Scripts](#Scripts)

We are going to treat this as a pipeline of Machine Learning (ML) models with swappable steps. This means that each step can be trained independently and implemented so that you can use appropriate models for any particular dataset.

## Find Labels

#### Get images

In production, providers will upload the herbarium sheets of interest. However, for model training we will download properly licensed labels for training the models ourselves.

#### What is a label?

We are currently considering a label as a separate piece of paper affixed to the herbarium sheet. Therefore, the stamp in the upper right corner or at the center near the bottom are not labels. We are also excluding rulers and color guides like the one at the bottom of the image. Other things not considered labels are envelopes containing plant parts, and any tags attached by string to the specimen. In this image, the labels are at the bottom right and include typewritten labels, handwritten labels, barcodes, and a QR-code.

Labels will be roughly aligned to the edges of the herbarium sheet itself.

#### Model training for finding labels

The strategy we are using for training this model is to download some herbarium sheets and have volunteers (citizen scientists) identify where the labels are and what type of writing they contain. We are using [Notes from Nature](https://www.zooniverse.org/organizations/md68135/notes-from-nature) to organize the data collection. Notes from Nature is a part of the [Zooniverse](https://www.zooniverse.org/).

We use [download_images.py](digi_leap/idigbio_images.py) (**TODO rewrite this script**) to download images for Notes from Nature "expeditions".

### Clean Labels

OCR engines are sensitive to noise, so we need to clean up the labels before we OCR them. Noise can be anything from stray marks and smudges, to underlined fields on the form that indicate where the field data should go, to rotated text.

See below for a label with underlines that will confound OCR engines.

![Figure 2: Label with underlines](assets/label_with_underlines.jpg)

## OCR Labels

- Train OCR engine for our uses.
- Adjust the set of OCR engine parameters.

### Clean OCR Text

OCR output is often dirty itself. There are spaces inside of words, and the engine may mistake one character for another. We need to clean up the text before performing Information Extraction (IE) on it.

## Extract Information

This is a project unto itself and is in another repository.

## Scripts

This is a list of the current set of scripts, what they do, and the general order to run them.

1. **dev_env.bash**: (optional) I use this to setup my personal development environment. You will likely want to use your own setup.
1. **idigbio_load.py**: (optional) iDigBio is a good source of data for both tests and extractions. Once you have downloaded the zip file use this script to load data into an SQLite database.
1. **idigbio_images.py**: (optional and incomplete). I use this script to mine iDigBio data for images of herbarium sheets and then download them for further use.
1. **itis_taxa.py**: I score the quality of the OCR by counting the number of words from an OCR label text that are in a vocabulary. I want to include taxon names in this vocabulary. To get them I download an ITIS SQLite database and extend the vocabulary with plant taxa from that database.
1. **label_babel_expedition.py**: (incomplete) I use this script to bundle the herbarium sheet images into a _Notes from Nature_ expedition that is used to create training data for the model(s) that finds labels on herbarium sheets.
1. **label_babel_reconcile.py**: We use _Notes from Nature_ to get training data for models that find labels on the herbarium sheets. For each herbarium sheet we have a few people mark all the labels they find. All of these labels have to be reconciled into a single "best" label.
1. ~~train_test_split.py~~: (optional) I use this simple script to spit that data from the last step into a training (training/validation) set and a holdout dataset for testing.
1. **faster_rcnn_train.py**: This is the script that trains a model that finds labels on herbarium sheets.
1. **faster_rcnn_test.py**: (optional) This tests the model we just trained above on the holdout dataset.
1. **faster_rcnn_use.py**: This script cuts labels out of the herbarium sheets.
1. **ocr_prepare.py**: This script takes the labels from the previous step and runs various image manipulations on them to make it easier to OCR them.
1. **ocr_labels.py**: This takes the prepared labels and runs the OCR engine on them, saving the text. I will run this script several times with varying conditions.
1. **ocr_ensemble.py**: I use all the OCR output from the last step as an ensemble to try to find a single "best" OCR output for each label, then I use that "best" label for further processing.
1. **ocr_score.py**: (optional) A script used report statistics on the ensemble output from the last step.
1. **TBD**: Is a script used to create a _Notes from Nature_ expedition used to locate problem areas in the OCR chain.
