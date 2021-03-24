# Digi-Leap
Extract information from images of herbarium specimen labels. To do this we need to convert labels on the images into text using optical character recognition (OCR) and then extract information form the text using natural language processing (NLP). We also need to prepare the data for the OCR and NLP steps.

Given an image like:

![Figure 1: Herbarium sample image](assets/herbarium_sample_image.jpg)

We want to:
1. [Find all the labels on the image.](#Find-Labels)
1. [Crop and clean up the labels so that we can OCR them.](#Clean-Labels)
1. [OCR the cleaned up label images.](#OCR-Labels)
1. [Cleanup the OCR text so that we can run NLP on it.](#Clean-OCR-Text)
1. [Use NLP to extract information from the clean OCR text.](#Extract-Information)

We are going to treat this as a pipeline of Machine Learning (ML) models with swappable steps. This means that each step may be independently trained and implemented so that appropriate models may be used for any particular dataset. A general strategy for the pipeline is to use as much as possible existing technology for each step.

## Find Labels

We are training a model to find labels on the herbarium sheet. We also want the model to identify the type of the label:
- Labels containing only typewritten text
- Labels containing only handwritten text
- Labels that contain both typewritten text and handwritten text
- Machine readable codes like barcodes and QR-codes

We are currently considering a label as a separate piece of paper affixed to the herbarium sheet. So the stamp in the upper right corner or at the center near the bottom are not considered a labels. We are also excluding rulers and color guides like the one at the bottom of the image. Other things not considered labels are envelopes containing plant parts, and any tags attached by string to the specimen. In the image, the labels are clustered at the bottom right and include typewritten labels, handwritten labels, barcodes, and a QR-code.

The strategy we are using for training this model is to download some herbarium sheets and have volunteers (citizen scientists) identify where the labels are on the sheet and what type of writing is on them. We are using [Notes from Nature](https://www.zooniverse.org/organizations/md68135/notes-from-nature) to organize the collection of the data. Notes from Nature is a part of the [Zooniverse](https://www.zooniverse.org/). We use [02_download_images.py](02_download_images.py) (**TODO rewrite**) to download images for Notes from Nature "expeditions".

## Clean Labels

The next desired step is to extract the text on the labels using OCR. However, open source OCR engines are quite sensitive to noise, so we need to clean up the labels before we OCR them. Noise can be anything from stray marks and smudges to underlined fields on the form that indicate where the data should go. See below for an of a label with underlines that will confound the OCR engine.


![Figure 2: Label with underlines](assets/label_with_underlines.jpg)

The training strategy for this step is to generate a bunch of fake labels and use them to train the models. The labels need to be "plausible looking" and don't have to be realistic. The advantages of this approach are that we always know what the ground truth (Y) is, and we can generate as many images as we need. The disadvantage is that we may generate augmented labels (X) that are not close enough to real ones to be useful. I.e. we may train for the wrong thing.

This itself involves a few steps:

1. Download data that can be used for label generation.
   - We download data in CSV format from [iDigBio](https://www.idigbio.org/portal/search).
   - We use [01_load_idigbio_data.py](01_load_idigbio_data.py) with these [arguments](args/01_load_idigbio_data.args) to load data that into a database.
1. Generate text for the images, mark on the label that text appears, and what kind of text it is (typewritten, handwritten, barcode, etc.).
   - [03_values_for_imputation.py](03_values_for_imputation.py) with these [arguments](args/03_values_for_imputation.args) samples the data from iDigBio so that we can impute certain label fields.
    - We then generate label text with [04_generate_label_text.py](04_generate_label_text.py) and these [arguments](args/04_generate_label_text.args).
1. We need to save that information to a database so that we can use it later for the OCR and OCR cleanup steps below.
1. We use [05_label_images.py](05_label_images.py) to generate both pristine versions of labels to use as targets for training the model (Y), and augmented versions of labels to use as model input (X). The Y dataset contains labels free of marks and underlines etc. We run this script at least 3 times:
   1. At least once to generate [training](args/05_train_images.args) data.
   1. At least once to generate [validation](args/05_valid_images.args) data. Validation data is used at the end of each epoch to test the progress of the training.
   1. At least once to generate [test](args/05_test_images.args) data. This is commonly called the holdout set.
1. We then use **TBD** to randomly augment images to make it look closer to a real label (X). This will include (but is not limited to) adding a color or gradient to the background, underlining some text, adding smudges, rotating the image, and adding stray marks, etc.
1. Finally, we can train the model to remove as many of the augmentations from above as possible.

*Note that we may also need to train separate models to do things like rotate the text to get it into a proper orientation for OCR etc.*

## OCR Labels

- Train OCR engine for our uses.
- Adjust the set of OCR engine parameters.

## Clean OCR Text

OCR output is often dirty itself. There are spaces inside of words, and the engine may mistake one character for another. We need to clean up the text before performing Information Extraction (IE) on it.

## Extract Information

This is a project unto itself and is in another repository.
