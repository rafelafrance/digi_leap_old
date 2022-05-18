create table if not exists sheets (
    sheet_id integer primary key autoincrement,
    path     text    unique,
    width    integer,
    height   integer,
    coreid   text,
    split    text
);
create unique index if not exists sheets_idx on sheets (coreid);


create table if not exists sheet_errors (
    error_id integer primary key autoincrement,
    path     text    unique
);


create table if not exists subjects_to_sheets (
    subject_id integer primary key,
    path       text,
    coreid     text
);
create index if not exists subs_to_sheets_idx on subjects_to_sheets (coreid);


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


create table if not exists consensus_text (
    consensus_id   integer primary key autoincrement,
    label_id       integer,
    consensus_set  text,
    ocr_set        text,
    consensus_text text
);
create index if not exists cons_label_id on consensus_text (label_id);


create table if not exists traits (
    trait_id     integer primary key autoincrement,
    trait_set    text,
    consensus_id text,
    method       text,
    trait        text,
    data         text
);
create index if not exists traits_trait_set on traits (trait_set);
create index if not exists traits_cons_id on traits (consensus_id);
create index if not exists traits_trait on traits (trait);


create table if not exists label_finder_tests (
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


create table if not exists runs (
    run_id integer primary key autoincrement,
    caller   text,
    args     text,
    comments text,
    started  date default (datetime('now','localtime')),
    finished date
);
