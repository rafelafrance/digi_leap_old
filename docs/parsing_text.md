# Parsing Herbarium Label Text

Here we describe a novel method for parsing herbarium label text that combines a rule-based parser (FloraTraiter) with a large language model (ChatGPT4).

The task is take text like this:
```
Herbarium of
San Diego State College
Erysimum capitatum (Dougl.) Greene.
Growing on bank beside Calif. Riding and
Hiking Trail north of Descanso.
13 May 1967 San Diego Co., Calif.
Coll: R.M. Beauchamp No. 484
```
And convert it into a machine-readable format like:
```json
{
    "dwc:eventDate": "1967-05-13",
    "dwc:verbatimEventDate": "13 May 1967",
    "dwc:country": "United States",
    "dwc:stateProvince": "California",
    "dwc:county": "San Diego",
    "dwc:recordNumber": "484",
    "dwc:verbatimLocality": "Bank beside California, Riding and Hiking Trail north of Descanso",
    "dwc:recordedBy": "R.M. Beauchamp",
    "dwc:scientificNameAuthorship": "Dougl Greene",
    "dwc:scientificName": "Erysimum capitatum (Dougl.) Greene",
    "dwc:taxonRank": "species"
}
```
Of course, the OCRed input text and the resulting JSON are not always this clean.

## Major processing steps

1. Given a text file with OCRed label text.
2. Use a rule-based parser to get one version of JSON output.
3. Use ChatGPT4 to parse the label.
4. Clean the ChatGPT4 output to get a second version of the JSON output.
5. Use heuristics to merge the two outputs into a single "best" JSON output.

### OCR input

For this process it is a given and label text from any source will do. Our programs require that the input text for each label is in its own text file.

We developed a pipeline that finds labels on herbarium sheets and uses an ensemble of image processing techniques and OCR engines to pull high quality text from herbarium labels. See [reference ourselves].

### Rule-based parsing

This parser was originally developed to parse plant treatments and was later adapted to parse label text. We use a multistep approach to parse text into traits.
