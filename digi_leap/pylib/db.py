"""Utilities for digi_leap.sqlite databases."""
import sqlite3


def select_records(database, sql, *, limit=0, **kwargs):
    """Get ocr_results records."""
    values, where = [], []

    for key, value in kwargs.items():
        key = key.strip("_")
        if value is None:
            pass
        elif isinstance(value, list) and value:
            where.append(f"{key} in ({','.join(['?'] * len(value))})")
            values += value
        else:
            where.append("{key} = ?")
            values.append(value)

    sql += (" where " + " and ".join(where)) if where else ""
    sql += f" limit {limit}" if limit else ""

    with sqlite3.connect(database) as cxn:
        cxn.row_factory = sqlite3.Row
        return cxn.execute(sql, values)


def insert_batch(database, sql, batch):
    """Insert a batch of sheets records."""
    if batch:
        with sqlite3.connect(database) as cxn:
            cxn.executemany(sql, batch)


def create_table(database, sql, table, *, drop=False):
    """Create a table with paths to the valid herbarium sheet images."""
    with sqlite3.connect(database) as cxn:
        if drop:
            cxn.executescript(f"""drop table if exists {table};""")

        cxn.executescript(sql)


# ############## Vocab table ##########################################################


def create_vocab_table(database, drop=False):
    """Create a table with vocabulary words and their frequencies."""
    sql = """
        create table if not exists vocab (
            word  text,
            freq  integer
        );
        """
    create_table(database, sql, "vocab", drop=drop)


def insert_vocabulary_words(database, batch):
    """Insert a batch of sheets records."""
    sql = """insert into vocab (word, freq) values (:word, :freq);"""
    insert_batch(database, sql, batch)


def select_vocab(database, limit=0):
    """Get herbarium sheet image data."""
    sql = """select * from vocab"""
    return select_records(database, sql, limit=limit)


# ############ Sheets tables ##########################################################


def create_sheets_table(database, drop=False):
    """Create a table with paths to the valid herbarium sheet images."""
    sql = """
        create table if not exists sheets (
            sheet_id integer primary key autoincrement,
            path     text    unique,
            width    integer,
            height   integer
        );
        """
    create_table(database, sql, "sheets", drop=drop)


def insert_sheets(database, batch):
    """Insert a batch of sheets records."""
    sql = "insert into sheets (path, width, height) values (:path, :width, :height);"
    insert_batch(database, sql, batch)


def create_sheet_errors_table(database, drop=False):
    """Create a table with paths to the invalid herbarium sheet images."""
    sql = """
        create table if not exists sheet_errors (
            error_id integer primary key autoincrement,
            path     text    unique
        );
        """
    create_table(database, sql, "sheet_errors", drop=drop)


def insert_sheet_errors(database, batch):
    """Insert a batch of sheets error records."""
    sql = """insert into sheet_errors (path) values (:path);"""
    insert_batch(database, sql, batch)


def select_sheets(database, limit=0):
    """Get herbarium sheet image data."""
    sql = """select * from sheets"""
    return select_records(database, sql, limit=limit)


# ############ label table ##########################################################


def create_label_table(database, drop=False):
    """Create a table with the label crops of the herbarium images."""
    sql = """
        create table if not exists labels (
            label_id     integer primary key autoincrement,
            sheet_id     integer,
            label_run    text,
            offset       integer,
            class        text,
            label_left   integer,
            label_top    integer,
            label_right  integer,
            label_bottom integer
        );

        create index if not exists labels_sheet_id on labels(sheet_id);
        """
    create_table(database, sql, "labels", drop=drop)


def insert_labels(database, batch):
    """Insert a batch of label records."""
    sql = """
        insert into labels
               ( sheet_id,    label_run,  offset,       class,
                 label_left,  label_top,  label_right,  label_bottom)
        values (:sheet_id,   :label_run, :offset,      :class,
                :label_left, :label_top, :label_right, :label_bottom);
    """
    insert_batch(database, sql, batch)


def select_labels(database, limit=0, label_runs=None, classes=None):
    """Get label records."""
    sql = """select * from labels join sheets using (sheet_id)"""
    return select_records(
        database, sql, limit=limit, class_=classes, label_run=label_runs
    )


# ############ ocr table #############################################################


def create_ocr_table(database, drop=False):
    """Create a table with the label crops of the herbarium images."""
    sql = """
        create table if not exists ocr (
            ocr_id     integer primary key autoincrement,
            label_id   integer,
            ocr_run    text,
            engine     text,
            pipeline   text,
            conf       real,
            ocr_left   integer,
            ocr_top    integer,
            ocr_right  integer,
            ocr_bottom integer,
            ocr_text   text
        );

        create index if not exists ocr_label_id on ocr(label_id);
        """
    create_table(database, sql, "ocr", drop=drop)


def insert_ocr(database, batch):
    """Insert a batch of ocr records."""
    sql = """
        insert into ocr
               ( labels_id, ocr_run,  engine,  pipeline,
                 conf,  ocr_left,  ocr_top,   ocr_right,   ocr_bottom,  ocr_text)
        values (:label_id, :ocr_run, :engine, :pipeline,
                :conf, :ocr_left, :ocr_top,  :ocr_right,  :ocr_bottom, :ocr_text);
    """
    insert_batch(database, sql, batch)


def select_ocr(database, ocr_runs=None, classes=None, limit=0):
    """Get ocr box records."""
    sql = """
        select *
          from ocr
          join labels using (label_id)
          join sheets using (sheet_id)
    """
    return select_records(database, sql, limit=limit, class_=classes, ocr_run=ocr_runs)


def get_ocr_runs(database):
    """Get all of the OCR runs in the database."""
    sql = """select distinct ocr_run from ocr"""
    return select_records(database, sql)


# ############ consensus table #######################################################


def create_cons_table(database, drop=False):
    """Create a table with the label crops of the herbarium images."""
    sql = """
        create table if not exists cons (
            cons_id   integer primary key autoincrement,
            label_id  integer,
            cons_run  text,
            ocr_run   text,
            cons_text text
        );
        create index if not exists cons_label_id on cons(label_id);
        """
    create_table(database, sql, "cons", drop=drop)


def insert_cons(database, batch):
    """Insert a batch of consensus records."""
    sql = """
        insert into cons
               ( label_id,  cons_run,  ocr_run,  cons_text)
        values (:label_id, :cons_run, :ocr_run, :cons_text);
    """
    insert_batch(database, sql, batch)


def select_cons(database, cons_runs=None, limit=0):
    """Get consensus records."""
    sql = """
        select *
          from cons
          join labels using (label_id)
          join sheets using (sheet_id)
    """
    return select_records(database, sql, limit=limit, cons_run=cons_runs)
