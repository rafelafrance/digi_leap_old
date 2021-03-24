# Digi-Leap
Extract information from images of herbarium specimen labels. To do this we need to convert labels on the images into text using optical character recognition (OCR) and then extract information form the text using natural language processing (NLP). We also need to prepare the data for the OCR and NLP steps.

Given an image like:

![Herbarium Sample Image](assets/herbarium_sample_image.jpg)

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

The strategy we are using for training this model is to download some herbarium sheets and have volunteers (citizen scientists) identify where the labels are on the sheet and what type of writing is on them. We are using [Notes from Nature](https://www.zooniverse.org/organizations/md68135/notes-from-nature) to organize the collection of the data. Notes from Nature is a part of the [Zooniverse](https://www.zooniverse.org/).\

## Clean Labels

The next desired step is to extract the text on the labels using OCR. However, open source OCR engines are quite sensitive to noise, so we need to clean up the labels before we OCR them. Noise can be anything from stray marks and smudges to underlined fields on the form that indicate where the data should go. See below for an of a label with underlines that will confound the OCR engine.

![image with underlines](assets/label_with_underlines.jpg)

TODO: A cleaned up version of this label.

The training strategy for this step is to generate a bunch of fake labels and use them to train the models. The labels need to be "plausible looking" and don't have to be realistic.

This itself involves a few steps:

1. Generate some text for the images and mark roughly where we place that text on the label and what kind of text it is (typewritten, handwritten, barcode, etc.).
1. We need to save that information to a database so that we can use it later for the OCR and OCR cleanup steps below.
1. We then generate an already cleaned version of the label to use as the target for training the model (Y). This image is free of marks and underlines and should look pristine.
1. We then randomly augment the image to make it look more like a real label (X). This will include (but is not limited to) adding a color to the background, underlines to some text, adding smudges, rotating the image, and stray marks, etc.
1. Finally, we can train the model to remove as many of the augmentations from above.

## OCR Labels

## Clean OCR Text

## Extract Information
