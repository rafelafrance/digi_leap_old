"""Utilities for digi_leap.sqlite databases."""
import inspect
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def connect(db_path):
    """Add a row factory to the normal connection context manager."""
    try:
        with sqlite3.connect(db_path) as cxn:
            cxn.row_factory = sqlite3.Row
            yield cxn
    finally:
        pass


def execute(cxn, sql, params=None):
    """Execute a query -- sugar for making database calls look the same."""
    return cxn.execute(sql, params)


# ############ Sheets tables ##########################################################
def create_sheets_table(cxn) -> None:
    sql = """
        create table if not exists sheets (
            sheet_id integer primary key autoincrement,
            path     text    unique,
            width    integer,
            height   integer,
            coreid   text,
            split    text
        );
        create unique index if not exists sheets_idx on sheets (coreid);
        """
    cxn.executescript(sql)


def create_sheet_errors_table(cxn) -> None:
    sql = """
        create table if not exists sheet_errors (
            error_id integer primary key autoincrement,
            path     text    unique
        );
        """
    cxn.executescript(sql)


# ############ label table ##########################################################
def create_label_table(cxn) -> None:
    sql = """
        create table if not exists labels (
            label_id     integer primary key autoincrement,
            sheet_id     integer,
            label_set    text,
            offset       integer,
            class        text,
            label_conf   real,
            label_left   integer,
            label_top    integer,
            label_right  integer,
            label_bottom integer
        );
        create unique index labels_idx on labels (label_set, sheet_id, offset);
        create index if not exists labels_sheet_id on labels(sheet_id);
        """
    cxn.executescript(sql)


def insert_labels(cxn, batch: list) -> None:
    sql = """
        insert into labels
               ( sheet_id,    label_set,  offset,       class,  label_conf,
                 label_left,  label_top,  label_right,  label_bottom)
        values (:sheet_id,   :label_set, :offset,      :class, :label_conf,
                :label_left, :label_top, :label_right, :label_bottom);
        """
    cxn.executemany(sql, batch)


def select_labels(cxn, label_set: str) -> list:
    sql = """select * from labels join sheets using (sheet_id) where label_set = ?"""
    return cxn.execute(sql, (label_set,))


def select_label_split(cxn, *, split: str, label_set: str) -> list:
    sql = """
        select * from sheets left join labels using (sheet_id)
         where split = ? and label_set = ?
        """
    return cxn.execute(sql, (split, label_set))


# ######### Subjects to sheets #######################################################
def create_subjects_to_sheets_table(cxn) -> None:
    sql = """
        create table if not exists subs_to_sheets (
            subject_id integer primary key,
            path       text,
            coreid     text
        );
        create index if not exists subs_to_sheets_idx on subs_to_sheets (coreid);
        """
    cxn.executescript(sql)


# ############ ocr table #############################################################
def create_ocr_table(cxn) -> None:
    sql = """
        create table if not exists ocr (
            ocr_id     integer primary key autoincrement,
            label_id   integer,
            ocr_set    text,
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
    cxn.executescript(sql)


def insert_ocr(cxn, batch: list) -> None:
    sql = """
        insert into ocr
               ( label_id,  ocr_set,  engine,  pipeline,
                 conf,  ocr_left,  ocr_top,   ocr_right,   ocr_bottom,  ocr_text)
        values (:label_id, :ocr_set, :engine, :pipeline,
                :conf, :ocr_left, :ocr_top,  :ocr_right,  :ocr_bottom, :ocr_text);
        """
    cxn.executemany(sql, batch)


def select_ocr(cxn, ocr_set) -> list:
    sql = """
        select *
          from ocr
          join labels using (label_id)
          join sheets using (sheet_id)
         where ocr_set = ?
        """
    return cxn.execute(sql, (ocr_set,))


def select_ocr_frags(cxn, ocr_set, label_id) -> list:
    sql = """
        select *
          from ocr
          join labels using (label_id)
          join sheets using (sheet_id)
         where ocr_set = ?
           and label_id = ?
        """
    return cxn.execute(sql, (ocr_set, label_id))


# ############ consensus table #######################################################
def create_consensus_table(cxn) -> None:
    sql = """
        create table if not exists cons (
            cons_id   integer primary key autoincrement,
            label_id  integer,
            cons_set  text,
            ocr_set   text,
            cons_text text
        );
        create index if not exists cons_label_id on cons (label_id);
        """
    cxn.executescript(sql)


def insert_consensus(cxn, batch: list) -> None:
    sql = """
        insert into cons
               ( label_id,  cons_set,  ocr_set,  cons_text)
        values (:label_id, :cons_set, :ocr_set, :cons_text);
        """
    cxn.executemany(sql, batch)


def select_consensus(cxn, cons_set: str) -> list:
    sql = """
        select *
          from cons
          join labels using (label_id)
          join sheets using (sheet_id)
         where cons_set = ?
        """
    return cxn.execute(sql, (cons_set,))


def sample_consensus(cxn, cons_set: str) -> list:
    sql = """
        select *
          from cons
          join labels using (label_id)
          join sheets using (sheet_id)
         where cons_set = ?
      order by random()
        """
    return cxn.execute(sql, (cons_set,))


# ############ traits table #########################################################
def create_traits_table(cxn) -> None:
    sql = """
        create table if not exists traits (
            trait_id  integer primary key autoincrement,
            trait_set text,
            cons_id   text,
            trait     text,
            data      text
        );
        create index if not exists traits_trait_set on traits (trait_set);
        create index if not exists traits_cons_id on traits (cons_id);
        create index if not exists traits_trait on traits (trait);
        """
    cxn.executescript(sql)


def insert_traits(cxn, batch: list) -> None:
    sql = """
        insert into traits
               ( trait_set,  cons_id,  trait,  data)
        values (:trait_set, :cons_id, :trait, :data);
    """
    cxn.executemany(sql, batch)


def select_traits(cxn, trait_set: str) -> list:
    sql = """
        select *
          from traits
          join cons using (cons_id)
          join labels using (label_id)
          join sheets using (sheet_id)
         where trait_set = ?
      order by cons_id, trait_id
        """
    return cxn.execute(sql, (trait_set,))


# ############ label finder test table ################################################
def create_tests_table(cxn) -> None:
    sql = """
        create table if not exists tests (
            test_id     integer primary key autoincrement,
            test_set    text,
            sheet_id    integer,
            pred_class  text,
            pred_conf   real,
            pred_left   integer,
            pred_top    integer,
            pred_right  integer,
            pred_bottom integer
        );
        """
    cxn.executescript(sql)


def insert_tests(cxn, batch: list) -> None:
    sql = """
        insert into tests
            ( test_set,   sheet_id,  pred_class,  pred_conf,
              pred_left,  pred_top,  pred_right,  pred_bottom)
     values (:test_set,  :sheet_id, :pred_class, :pred_conf,
             :pred_left, :pred_top, :pred_right, :pred_bottom);"""
    cxn.executemany(sql, batch)


# ######################### runs table ################################################
def create_runs_table(cxn) -> None:
    sql = """
        create table if not exists runs (
            run_id integer primary key autoincrement,
            caller   text,
            args     text,
            comments text,
            started  date default (datetime('now','localtime')),
            finished date
        );
        """
    cxn.executescript(sql)


def insert_run(cxn, args, comments: str = "") -> int:
    create_runs_table(cxn)

    __, file, line, func, *_ = inspect.stack()[1]
    caller = f"file name: {Path(file).name}, function: {func}, line: {line}"

    json_args = json.dumps({k: str(v) for k, v in vars(args).items()})

    sql = """
        insert into runs ( caller,  args,  comments)
                  values (:caller, :args, :comments);
        """
    cxn.execute(sql, (caller, json_args, comments))
    results = cxn.execute("select seq from sqlite_sequence where name = 'runs';")

    return results.fetchone()[0]


def update_run_finished(cxn, run_id: int):
    sql = """
        update runs set finished = datetime('now', 'localtime') where run_id = ?
        """
    cxn.execute(sql, (run_id,))


def update_run_comments(cxn, run_id: int, comments: str):
    sql = """
        update runs set comments = ?, finished = datetime('now', 'localtime')
         where run_id = ?"""
    cxn.execute(sql, (comments, run_id))
