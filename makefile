DATE=`date +%Y-%m-%d`
PROCESSED=./data/processed
TEMP=./data/temp
LABEL_DB=label_data.sqlite.db
DB_NAME="$(PROCESSED)/$(LABEL_DB)"
DB_BACKUP="$(PROCESSED)/$(basename $(LABEL_DB))_$(DATE).db"
PYTHON=python
SRC=./digi_leap

data:
	$(PYTHON) $(SRC)/01_download_images.py
	$(PYTHON) $(SRC)/02_load_idigbio_data.py
	$(PYTHON) $(SRC)/03_generate_label_data.py
	$(PYTHON) $(SRC)/04_augment_label_data.py

clean:
	rm ${TEMP}/*

backup:
	cp $(LABEL_DB) $(LABEL_DB)
