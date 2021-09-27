"""Command line arguments."""

from pathlib import Path

DEFAULT = {
    # Root dir for the label babel data
    "label_babel_dir": {
        "type": Path,
        "help": "Base directory for Label Babel data.",
    },
    # The most recent models
    "curr_model_name": {
        "default": "faster_rcnn_2021-08-18",
        "help": "The name of the model being used to find labels on herbarium sheets.",
    },
    "prev_model_name": {
        "type": Path,
        "help": "Name of the model previous used to find labels on herbarium sheets.",
    },
    "image_filter": {
        "default": "*.jpg",
        "help": "Glob images in the given directory with this pattern.",
    },
    # GPU jobs
    "device": {
        "default": "cuda:0",
        "help": "Which GPU or CPU to use. Options are 'cpu', 'cuda:0', 'cuda:1', etc.",
    },
    "gpu_batch": {
        "default": 2,
        "help": "Input batch size for model batches.",
    },
    "workers": {
        "default": 2,
        "help": "Number of workers for loading data.",
    },
    # Processes and threads
    "proc_cpus": {
        "default": 6,
        "help": "How many process to spawn for running this job.",
    },
    "proc_batch": {
        "default": 10,
        "help": "How many items to put in each spawned CPU batch.",
    },
    "threads": {
        "default": 20,
        "help": "",
    },
    "row_batch": {
        "default": 1_000_000,
        "help": "Batch size when loading large data sets.",
    },
    "nms_threshold": {
        "default": 0.3,
        "help": "IoU overlap to use for non-maximum suppression.",
    },
    "sbs_threshold": {
        "default": 0.95,
        "help": "IoU overlap to use for small box suppression",
    },
    "limit": {
        "type": int,
        "help": "Limit the input to this many records.",
    },
    "label_babel": {
        "default": "17633_label_babel_2",
        "help": "Name of a Label Babel expedition.",
    },
    "sheets_dir": {
        "type": Path,
        "help": "The directory containing the herbarium sheet images.",
    },
    "unreconciled_csv": {
        "type": Path,
        "help": "Unreconciled CSV data from a Label Babel expedition.",
    },
    "reconciled_jsonl": {
        "type": Path,
        "help": "Reconciled JSONL data from a Label Babel expedition.",
    },
    "prep_dir": {
        "type": Path,
        "help": "The directory that holds prepared label images.",
    },
    "ensemble_image_dir": {
        "type": Path,
        "help": "OCR ensemble images are in this directory.",
    },
    "ensemble_text_dir": {
        "type": Path,
        "help": "OCR ensemble text is in directory.",
    },
    "idigbio_db": {
        "default": Path,
        "help": "Database that holds processed iDigBio data.",
    },
    "idigbio_zip_file": {
        "type": Path,
        "help": "Zip file that holds raw iDigBio data.",
    },
    "itis_db": {
        "type": Path,
        "help": "ITIS database.",
    },
    "label_dir": {
        "type": Path,
        "help": "Directory containing cropped labels from herbarium sheets.",
    },
    "curr_model": {
        "type": Path,
        "help": "Path, to the current model for finding labels on a herbarium sheet.",
    },
    "pipeline": {
        "default": "deskew",
        "help": "A pipeline of image transformations that help with the OCR process.",
    },
    "ocr_engine": {
        "default": "tesseract",
        "choices": ["tesseract", "easyocr"],
        "help": "Which OCR engine to use.",
    },
}

# ###################################################################################
# Default arguments for scripts

ARGS = {
    "faster_rcnn_test": {
        "help": """Test a model that finds labels on herbarium sheets
            (inference with scoring).""",
        "reconciled_jsonl": DEFAULT["reconciled_jsonl"],
        "sheets_dir": DEFAULT["sheets_dir"],
        "load_model": DEFAULT["curr_model"],
        "nms_threshold": DEFAULT["nms_threshold"],
        "sbs_threshold": DEFAULT["sbs_threshold"],
        "device": DEFAULT["device"],
        "batch_size": DEFAULT["gpu_batch"],
        "workers": DEFAULT["workers"],
        "limit": DEFAULT["limit"],
    },
    "faster_rcnn_train": {
        "help": """Train a model to find labels on herbarium sheets.""",
        "reconciled_jsonl": DEFAULT["reconciled_jsonl"],
        "sheets_dir": DEFAULT["sheets_dir"],
        "save_model": DEFAULT["curr_model"],
        "load_model": {
            "default": "",
            "help": "Load this model to continue training.",
        },
        "batch_size": DEFAULT["gpu_batch"],
        "device": DEFAULT["device"],
        "nms_threshold": DEFAULT["nms_threshold"],
        "sbs_threshold": DEFAULT["sbs_threshold"],
        "workers": DEFAULT["workers"],
        "limit": DEFAULT["limit"],
        "epochs": {
            "default": 100,
            "help": "How many epochs for training the model.",
        },
        "learning_rate": {
            "default": 0.005,
            "help": "The learning rate for training the model.",
        },
        "split": {
            "default": 0.25,
            "help": "The train/validation split for training the model.",
        },
    },
    "faster_rcnn_use": {
        "help": """Use a model that finds labels on herbarium sheets (inference).""",
        "sheets_dir": DEFAULT["sheets_dir"],
        "label_dir": DEFAULT["label_dir"],
        "glob": DEFAULT["image_filter"],
        "load_model": DEFAULT["curr_model"],
        "device": DEFAULT["device"],
        "nms_threshold": DEFAULT["nms_threshold"],
        "sbs_threshold": DEFAULT["sbs_threshold"],
        "limit": DEFAULT["limit"],
    },
    "idigbio_images": {
        "help": """
    Use iDigBio records to download images. You should extract an iDigBio media
    file from a snapshot before running this.""",
        "sheets_dir": DEFAULT["sheets_dir"],
        "csv_file": {
            "default": "data/sernec/sernec_multimedia.csv",
            "help": "The CSV file that contains the image URLs.",
        },
        "sample_size": {
            "default": 10_000,
            "help": "How many records to sample from the CSV file.",
        },
        "url_column": {
            "default": "accessURI",
            "help": "Which column contains the image URI.",
        },
    },
    "idigbio_load": {
        "zip_file": DEFAULT["idigbio_zip_file"],
        "database": DEFAULT["idigbio_db"],
        "batch": DEFAULT["row_batch"],
        "csv_file": {
            "default": "occurrence_raw.csv",
            "help": "The raw CSV file inside of the zip file.",
        },
        "table_name": {
            "default": "occurrence_raw",
            "help": "What to call the table containing the processed data.",
        },
        "col_filters": {
            "default": ["."],
            "help": "Which columns to extract from the raw CSV file.",
        },
        "row_filters": {
            "default": ["plant@dwc:kingdom", ".@dwc:scientificName"],
            "help": "Filter rows in the raw CSV file.",
        },
    },
    "itis_taxa": {
        "lang": {
            "default": "en_US",
            "help": "",
        },
    },
    "label_babel_reconcile": {
        "nothing": {
            "help": "",
        },
    },
    "ocr_ensemble": {
        "help": """Build a single "best" label from the ensemble of OCR outputs.
            An ensemble is a list of OCR outputs with the same name contained
            in parallel directories. For instance, if you have OCR output
            (from the ocr_labels action) for three different runs then an ensemble
            will be:
                output/ocr/run1/label1.csv
                output/ocr/run2/label1.csv
                output/ocr/run3/label1.csv
                """,
        "ocr_dir": {
            "default": "output/ocr_*",
            "help": "The set of OCR output directories to use for the ensemble.",
        },
        "label_filter": {},
        "ensemble_text": DEFAULT["ensemble_text_dir"],
        "prepared_dir": DEFAULT["prep_dir"],
        "winners_jsonl": {
            "type": Path,
            "help": "Save data on which OCR results were used in the output.",
        },
        "cpus": DEFAULT["proc_cpus"],
        "batch_size": DEFAULT["proc_batch"],
        "limit": DEFAULT["limit"],
        "line_space": {
            "default": 8,
            "help": "Margin between lines of text in the reconstructed label output.",
        },
    },
    "ocr_expedition": {
        "ensemble_images": DEFAULT["ensemble_image_dir"],
        "ensemble_text": DEFAULT["ensemble_text_dir"],
        "label_dir": DEFAULT["label_dir"],
        "expedition_dir": {
            "type": Path,
            "help": "Where the expedition files are.",
        },
        "filter_rulers": {
            "default": 2.0,
            "help": """Consider a label to be a ruler if the height:width
                (or width:height) ratio is above this.""",
        },
        "largest_labels": {
            "default": 1,
            "help": "Keep the N largest labels.",
        },
        "word_count_threshold": {
            "default": 20,
            "help": "Skip labels with fewer than this many words.",
        },
        "vocab_count_threshold": {
            "default": 10,
            "help": "Skip labels with fewer than this vocabulary hits.",
        },
        "filter_types": {
            "default": ["Barcode", "Both", "Handwritten"],
            "help": "Remove labels if they fall into any of these categories.",
        },
    },
    "ocr_in_house_qc": {
        "help": """Build a single "best" label from the ensemble of OCR outputs.""",
        "qc_dir": {
            "type": Path,
            "help": "",
        },
        "ensemble_images": DEFAULT["ensemble_image_dir"],
        "ensemble_text": DEFAULT["ensemble_text_dir"],
        "reconciled_jsonl": DEFAULT["reconciled_jsonl"],
        "sheets_dir": DEFAULT["sheets_dir"],
        "sample_size": {
            "default": 25,
            "help": "",
        },
    },
    "ocr_labels": {
        "help": """OCR images of labels.""",
        "prepared_dir": DEFAULT["prep_dir"],
        "output_dir": {
            "type": Path,
            "help": "Put OCR output for labels into this directory.",
        },
        "ocr_engine": DEFAULT["ocr_engine"],
        "glob": DEFAULT["image_filter"],
        "cpus": DEFAULT["proc_cpus"],
        "batch_size": DEFAULT["proc_batch"],
        "limit": DEFAULT["limit"],
    },
    "ocr_prepare": {
        "help": """Prepare images of labels for OCR. Perform image manipulations on
            labels that may help with the OCR process.""",
        "label_dir": DEFAULT["label_dir"],
        "output_dir": DEFAULT["prep_dir"],
        "pipeline": DEFAULT["pipeline"],
        "cpus": DEFAULT["proc_cpus"],
        "batch_size": DEFAULT["proc_batch"],
        "glob": DEFAULT["image_filter"],
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
