"""Command line arguments."""

from pathlib import Path

DEFAULT = {
    # Root dir for the label babel data
    "label-babel-dir": {
        "type": Path,
        "help": "Base directory for Label Babel data.",
    },
    # The most recent models
    "curr-model-name": {
        "default": "faster_rcnn_2021-08-18",
        "help": "The name of the model being used to find labels on herbarium sheets.",
    },
    "prev-model-name": {
        "type": Path,
        "help": "Name of the model previous used to find labels on herbarium sheets.",
    },
    "image-filter": {
        "default": "*.jpg",
        "help": "Glob images in the given directory with this pattern.",
    },
    # GPU jobs
    "device": {
        "default": "cuda:0",
        "help": "Which GPU or CPU to use. Options are 'cpu', 'cuda:0', 'cuda:1', etc.",
    },
    "gpu-batch": {
        "default": 2,
        "help": "Input batch size for model batches.",
    },
    "workers": {
        "default": 2,
        "help": "Number of workers for loading data.",
    },
    # Processes and threads
    "proc-cpus": {
        "default": 6,
        "help": "How many process to spawn for running this job.",
    },
    "proc-batch": {
        "default": 10,
        "help": "How many items to put in each spawned CPU batch.",
    },
    "threads": {
        "default": 20,
        "help": "",
    },
    "row-batch": {
        "default": 1_000_000,
        "help": "Batch size when loading large data sets.",
    },
    "nms-threshold": {
        "default": 0.3,
        "help": "IoU overlap to use for non-maximum suppression.",
    },
    "sbs-threshold": {
        "default": 0.95,
        "help": "IoU overlap to use for small box suppression",
    },
    "limit": {
        "type": int,
        "help": "Limit the input to this many records.",
    },
    "label-babel": {
        "default": "17633_label_babel_2",
        "help": "Name of a Label Babel expedition.",
    },
    "sheets-dir": {
        "type": Path,
        "help": "The directory containing the herbarium sheet images.",
    },
    "unreconciled-csv": {
        "type": Path,
        "help": "Unreconciled CSV data from a Label Babel expedition.",
    },
    "reconciled-jsonl": {
        "type": Path,
        "help": "Reconciled JSONL data from a Label Babel expedition.",
    },
    "prep-dir": {
        "type": Path,
        "help": "The directory that holds prepared label images.",
    },
    "ensemble-image-dir": {
        "type": Path,
        "help": "OCR ensemble images are in this directory.",
    },
    "ensemble-text-dir": {
        "type": Path,
        "help": "OCR ensemble text is in directory.",
    },
    "idigbio-db": {
        "type": Path,
        "help": "Database that holds processed iDigBio data.",
    },
    "idigbio-zip-file": {
        "type": Path,
        "help": "Zip file that holds raw iDigBio data.",
    },
    "itis-db": {
        "type": Path,
        "help": "ITIS database.",
    },
    "label-dir": {
        "type": Path,
        "help": "Directory containing cropped labels from herbarium sheets.",
    },
    "curr-model": {
        "type": Path,
        "help": "Path, to the current model for finding labels on a herbarium sheet.",
    },
    "pipeline": {
        "default": "deskew",
        "help": "A pipeline of image transformations that help with the OCR process.",
    },
    "ocr-engine": {
        "default": "tesseract",
        "choices": ["tesseract", "easyocr"],
        "help": "Which OCR engine to use.",
    },
}

# ###################################################################################
# Default arguments for scripts

ARGS = {
    "faster-rcnn-test": {
        "help": """Test a model that finds labels on herbarium sheets
                   (inference with scoring).""",
        "reconciled-jsonl": DEFAULT["reconciled-jsonl"],
        "sheets-dir": DEFAULT["sheets-dir"],
        "load-model": DEFAULT["curr-model"],
        "nms-threshold": DEFAULT["nms-threshold"],
        "sbs-threshold": DEFAULT["sbs-threshold"],
        "device": DEFAULT["device"],
        "batch-size": DEFAULT["gpu-batch"],
        "workers": DEFAULT["workers"],
        "limit": DEFAULT["limit"],
    },
    "faster-rcnn-train": {
        "help": """Train a model to find labels on herbarium sheets.""",
        "reconciled-jsonl": DEFAULT["reconciled-jsonl"],
        "sheets-dir": DEFAULT["sheets-dir"],
        "save-model": DEFAULT["curr-model"],
        "load-model": {
            "default": "",
            "help": "Load this model to continue training.",
        },
        "batch-size": DEFAULT["gpu-batch"],
        "device": DEFAULT["device"],
        "nms-threshold": DEFAULT["nms-threshold"],
        "sbs-threshold": DEFAULT["sbs-threshold"],
        "workers": DEFAULT["workers"],
        "limit": DEFAULT["limit"],
        "epochs": {
            "default": 100,
            "help": "How many epochs for training the model.",
        },
        "learning-rate": {
            "default": 0.005,
            "help": "The learning rate for training the model.",
        },
        "split": {
            "default": 0.25,
            "help": "The train/validation split for training the model.",
        },
    },
    "faster-rcnn-use": {
        "help": """Use a model that finds labels on herbarium sheets (inference).""",
        "sheets-dir": DEFAULT["sheets-dir"],
        "label-dir": DEFAULT["label-dir"],
        "glob": DEFAULT["image-filter"],
        "load-model": DEFAULT["curr-model"],
        "device": DEFAULT["device"],
        "nms-threshold": DEFAULT["nms-threshold"],
        "sbs-threshold": DEFAULT["sbs-threshold"],
        "limit": DEFAULT["limit"],
    },
    "idigbio-images": {
        "help": """Use iDigBio records to download images. You should extract an
                   DigBio media file from a snapshot before running this.""",
        "sheets-dir": DEFAULT["sheets-dir"],
        "csv-file": {
            "default": "data/sernec/sernec_multimedia.csv",
            "help": "The CSV file that contains the image URLs.",
        },
        "sample-size": {
            "default": 10_000,
            "help": "How many records to sample from the CSV file.",
        },
        "url-column": {
            "default": "accessURI",
            "help": "Which column contains the image URI.",
        },
    },
    "idigbio-load": {
        "zip-file": DEFAULT["idigbio-zip-file"],
        "database": DEFAULT["idigbio-db"],
        "batch": DEFAULT["row-batch"],
        "csv-file": {
            "default": "occurrence_raw.csv",
            "help": "The raw CSV file inside of the zip file.",
        },
        "table-name": {
            "default": "occurrence_raw",
            "help": "What to call the table containing the processed data.",
        },
        "col-filters": {
            "nargs": "*",
            "default": ["."],
            "help": "Which columns to extract from the raw CSV file.",
        },
        "row-filters": {
            "nargs": "*",
            "default": ["plant@dwc:kingdom", ".@dwc:scientificName"],
            "help": "Filter rows in the raw CSV file.",
        },
    },
    "itis-taxa": {
        "lang": {
            "default": "en_US",
            "help": "",
        },
    },
    "label-babel-reconcile": {
        "nothing": {
            "help": "",
        },
    },
    "ocr-ensemble": {
        "help": """Build a single "best" label from the ensemble of OCR outputs.
                   An ensemble is a list of OCR outputs with the same name contained
                   in parallel directories. For instance, if you have OCR output
                   (from the ocr-labels action) for three different runs then an
                   ensemble will be:
                        output/ocr/run1/label1.csv
                        output/ocr/run2/label1.csv
                        output/ocr/run3/label1.csv
                """,
        "ocr-dir": {
            "default": "output/ocr_*",
            "help": "The set of OCR output directories to use for the ensemble.",
        },
        "label-filter": {},
        "ensemble-text": DEFAULT["ensemble-text-dir"],
        "prepared-dir": DEFAULT["prep-dir"],
        "winners-jsonl": {
            "type": Path,
            "help": "Save data on which OCR results were used in the output.",
        },
        "cpus": DEFAULT["proc-cpus"],
        "batch-size": DEFAULT["proc-batch"],
        "limit": DEFAULT["limit"],
        "line-space": {
            "default": 8,
            "help": "Margin between lines of text in the reconstructed label output.",
        },
    },
    "ocr-expedition": {
        "ensemble-images": DEFAULT["ensemble-image-dir"],
        "ensemble-text": DEFAULT["ensemble-text-dir"],
        "label-dir": DEFAULT["label-dir"],
        "expedition-dir": {
            "type": Path,
            "help": "Where the expedition files are.",
        },
        "filter-rulers": {
            "default": 2.0,
            "help": """Consider a label to be a ruler if the height:width
                      (or width:height) ratio is above this.""",
        },
        "largest-labels": {
            "default": 1,
            "help": "Keep the N largest labels.",
        },
        "word-count-threshold": {
            "default": 20,
            "help": "Skip labels with fewer than this many words.",
        },
        "vocab-count-threshold": {
            "default": 10,
            "help": "Skip labels with fewer than this vocabulary hits.",
        },
        "filter-types": {
            "choices": ["Barcode", "Handwritten", "Typewritten", "Both"],
            "nargs": "*",
            "default": ["Typewritten"],
            "help": "Keep labels if they fall into any of these categories.",
        },
    },
    "ocr-in-house-qc": {
        "help": """Build a single "best" label from the ensemble of OCR outputs.""",
        "qc-dir": {
            "type": Path,
            "help": "",
        },
        "ensemble-images": DEFAULT["ensemble-image-dir"],
        "ensemble-text": DEFAULT["ensemble-text-dir"],
        "reconciled-jsonl": DEFAULT["reconciled-jsonl"],
        "sheets-dir": DEFAULT["sheets-dir"],
        "sample-size": {
            "default": 25,
            "help": "",
        },
    },
    "ocr-labels": {
        "help": """OCR images of labels.""",
        "prepared-dir": DEFAULT["prep-dir"],
        "output-dir": {
            "type": Path,
            "help": "Put OCR output for labels into this directory.",
        },
        "ocr-engine": DEFAULT["ocr-engine"],
        "glob": DEFAULT["image-filter"],
        "cpus": DEFAULT["proc-cpus"],
        "batch-size": DEFAULT["proc-batch"],
        "limit": DEFAULT["limit"],
    },
    "ocr-prepare": {
        "help": """Prepare images of labels for OCR. Perform image manipulations on
                   labels that may help with the OCR process.""",
        "label-dir": DEFAULT["label-dir"],
        "output-dir": DEFAULT["prep-dir"],
        "pipeline": DEFAULT["pipeline"],
        "cpus": DEFAULT["proc-cpus"],
        "batch-size": DEFAULT["proc-batch"],
        "glob": DEFAULT["image-filter"],
        "limit": DEFAULT["limit"],
    },
}


def display(args):
    """Format arguments for the screen."""
    for arg, settings in args.items():
        if isinstance(settings, dict):
            print(f"    {arg}")
            for key, value in settings.items():
                if key == 'type':
                    value = str(value).replace("<class '", "").replace("'>", "")
                print(f"        {key:<12} {value}")


def update_defaults(defaults):
    """Update arguments with reasonable defaults."""
    for name, params in defaults.items():

        if defaults[name].get('help') and 'default' in params:
            defaults[name]['help'] += f" (default {defaults[name]['default']})"


def update_args(args):
    """Update arguments with reasonable defaults."""
    for action, params in args.items():
        for name, arg in params.items():

            # Skip module help
            if name == 'help':
                continue

            # Process the argument
            if 'type' not in arg and 'default' in arg:
                params[name]['type'] = type(params[name]['default'])


update_defaults(DEFAULT)
update_args(ARGS)
