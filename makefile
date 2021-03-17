DATE=`date +%Y-%m-%d`
SCRIPT_DIR=.
PROCESSED_DIR=./data/processed
TEMP_DIR=./data/temp
ARGS_DIR=./args
DB_NAME=label_data.sqlite.db
LABEL_DB="$(PROCESSED_DIR)/$(LABEL_DB)"
BACKUP_DB="$(PROCESSED_DIR)/$(basename $(DB_NAME))_$(DATE).db"
PYTHON=python

label_images:
	$(PYTHON) $(SCRIPT_DIR)/05_label_images.py @$(ARGS_DIR)/05_label_images.args

label_text:
	$(PYTHON) $(SCRIPT_DIR)/04_generate_label_text.py @$(ARGS_DIR)/04_generate_label_data.args

idigbio_data:
	$(PYTHON) $(SCRIPT_DIR)/01_load_idigbio_data.py @$(ARGS_DIR)/01_idigbio_occurrence_raw.args
	$(PYTHON) $(SCRIPT_DIR)/03_values_for_imputation.py @$(ARGS_DIR)/03_values_for_imputation.args

download_images:
	$(PYTHON) $(SCRIPT_DIR)/02_download_images.py

clean:
	rm $(TEMP_DIR)/*

backup:
	cp $(LABEL_DB) $(BACKUP_DB)
