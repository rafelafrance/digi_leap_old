DATE=`date +%Y-%m-%d`
PROCESSED=./data/processed
TEMP=./data/temp
DB_NAME=label_data.sqlite.db
LABEL_DB="$(PROCESSED)/$(LABEL_DB)"
BACKUP_DB="$(PROCESSED)/$(basename $(DB_NAME))_$(DATE).db"
PYTHON=python
SRC=./digi_leap

label_text:
	$(PYTHON) $(SRC)/05_generate_label_text.py

label_data:
	$(PYTHON) $(SRC)/03_generate_label_data.py
	$(PYTHON) $(SRC)/04_augment_label_data.py

idigbio_data:
	$(PYTHON) $(SRC)/02_load_idigbio_data.py

images:
	$(PYTHON) $(SRC)/01_download_images.py

clean:
	rm ${TEMP}/*

backup:
	cp $(LABEL_DB) $(BACKUP_DB)
