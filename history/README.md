# Digi-Leap
Extract information from images of herbarium specimen labels. To do this we need to convert labels on the images into text using optical character recognition (OCR) and then extract information form the text using natural language processing (NLP). There are other steps in between to make these larger goals possible.

Given an image like:

![Figure 1: Herbarium sample image](assets/herbarium_sample_image.jpg)

We want to:
1. [Find all the labels on the image.](#Find-Labels)
   1. [Cutout and clean up the labels so that we can OCR them.](#Clean-Labels)
1. [OCR the cleaned up label images.](#OCR-Labels)
   1. [Cleanup the OCR text so that we can run NLP on it.](#Clean-OCR-Text)
1. [Use NLP to extract information from the clean OCR text.](#Extract-Information)

We are going to treat this as a pipeline of Machine Learning (ML) models with swappable steps. This means that each step may be independently trained and implemented so that appropriate models may be used for any particular dataset. A general strategy for the pipeline is to use, as much as possible, existing open source libraries for each step.


## Find Labels

#### Get images

In production, providers will upload the herbarium sheets of interest. However, for model training we will download properly licensed labels for training the models ourselves.

#### What is a label?

We are currently considering a label as a separate piece of paper affixed to the herbarium sheet. So the stamp in the upper right corner or at the center near the bottom are not considered labels. We are also excluding rulers and color guides like the one at the bottom of the image. Other things not considered labels are envelopes containing plant parts, and any tags attached by string to the specimen. In this image, the labels are clustered at the bottom right and include typewritten labels, handwritten labels, barcodes, and a QR-code.

Labels will be roughly aligned to the edges of the herbarium sheet itself.

#### Model training for finding labels

The strategy we are using for training this model is to download some herbarium sheets and have volunteers (citizen scientists) identify where the labels are on the sheet and what type of writing is on them. We are using [Notes from Nature](https://www.zooniverse.org/organizations/md68135/notes-from-nature) to organize the data collection. Notes from Nature is a part of the [Zooniverse](https://www.zooniverse.org/).

We use [02_download_images.py](download_images.py) (**TODO rewrite this script**) to download images for Notes from Nature "expeditions".

### Clean Labels

OCR engines are sensitive to noise, so we need to clean up the labels before we OCR them. Therefore, we **cutout** the labels from the original image and **clean** them before feeding them into the OCR engine. Noise can be anything from stray marks and smudges, to underlined fields on the form that indicate where the field data should go, to rotated text.

See below for a label with underlines that will confound OCR engines.

![Figure 2: Label with underlines](assets/label_with_underlines.jpg)

#### Training strategy

The training strategy is to generate a bunch of fake labels and use them to train the models. The labels need to be "plausible looking" and don't have to be realistic. The advantages of this approach are that we always know what the ground truth (Y) is, we can save this data for future steps, and we can generate as many images as we need. The disadvantage is that we may generate augmented labels (X) that are not close enough to real ones to be useful. I.e. we may train for the wrong thing.

#### Model training for cleaning labels

1. Download data that can be used for label generation.
   - We download data in CSV format from [iDigBio](https://www.idigbio.org/portal/search).
   - We use [01_load_idigbio_data.py](load_idigbio_data.py) with these [arguments](args/load_idigbio_data.args) to load data that into a database.
1. Generate text for the images, mark where on the label that text appears, and what kind of text it is (typewritten, handwritten, barcode, etc.).
   - [03_values_for_imputation.py](values_for_imputation.py) with these [arguments](args/values_for_imputation.args) samples the data from iDigBio so that we can impute certain label fields.
    - We then generate label text with [04_generate_label_text.py](generate_label_text.py) and these [arguments](args/generate_label_text.args).
1. We save that information to a database so that we can use it later for the OCR and OCR cleanup steps below.
1. We use [05_label_images.py](label_images.py) to generate both pristine versions of labels to use as targets for training the model (Y), and augmented versions of labels to use as model input (X). The Y dataset contains labels free of marks and underlines etc. We run this script at least 3 times:
   1. At least once to generate [training](args/train_images.args) data.
   1. At least once to generate [validation](args/valid_images.args) data. Validation data is used at the end of each epoch to test the progress of the training.
   1. At least once to generate [test](args/test_images.args) data. This is commonly called the holdout set.
1. We then use **TBD** to randomly augment images to make it look closer to a real label (X). This will include (but is not limited to) adding a color or gradient to the background, underlining some text, adding smudges, rotating the image, and adding stray marks, etc.
1. Next, we can train the model to remove as many of the augmentations from above as possible.
1. Finally, we examine how well the cleanup worked on both the generated fake labels and, more importantly, on real labels cut out from the actual herbarium sheets.

*Note that we may also need to train separate models to do things like rotate the text to get it into a proper orientation for OCR etc.*

## OCR Labels

- Train OCR engine for our uses.
- Adjust the set of OCR engine parameters.

### Clean OCR Text

OCR output is often dirty itself. There are spaces inside of words, and the engine may mistake one character for another. We need to clean up the text before performing Information Extraction (IE) on it.

## Extract Information

This is a project unto itself and is in another repository.
