CANNED_INSERTS = {
    "labels": """
        insert into labels
               ( sheet_id,    label_set,  offset,       class,  label_conf,
                 label_left,  label_top,  label_right,  label_bottom)
        values (:sheet_id,   :label_set, :offset,      :class, :label_conf,
                :label_left, :label_top, :label_right, :label_bottom);
        """,
    "ocr": """
        insert into ocr
               ( label_id,  ocr_set,  engine,  pipeline,  conf,
                 ocr_left,  ocr_top,   ocr_right,   ocr_bottom,  ocr_text)
        values (:label_id, :ocr_set, :engine, :pipeline, :conf,
                :ocr_left, :ocr_top,  :ocr_right,  :ocr_bottom, :ocr_text);
        """,
    "consensus_text": """
        insert into consensus_text
                         ( label_id,  consensus_set,  ocr_set,  consensus_text)
                  values (:label_id, :consensus_set, :ocr_set, :consensus_text);
        """,
    "traits": """
        insert into traits ( trait_set,  consensus_id,  trait,  data)
                    values (:trait_set, :consensus_id, :trait, :data);
        """,
    "label_finder_tests": """
        insert into label_finder_tests
               ( test_set,   sheet_id,  pred_class,  pred_conf,
                 pred_left,  pred_top,  pred_right,  pred_bottom)
        values (:test_set,  :sheet_id, :pred_class, :pred_conf,
                :pred_left, :pred_top, :pred_right, :pred_bottom);
        """,
}

CANNED_SELECTS = {
    "labels": """
        select *
        from   labels
        join   sheets using (sheet_id)
        where  label_set = :label_set;
        """,
    "label_split": """
        select    *
        from      sheets
        left join labels using (sheet_id)
        where     split = :split
        and       label_set = :label_set;
        """,
    "ocr": """
        select *
        from   ocr
        join   labels using (label_id)
        join   sheets using (sheet_id)
        where  ocr_set = :ocr_set;
        """,
    "consensus_text": """
        select *
        from   consensus_text
        join   labels using (label_id)
        join   sheets using (sheet_id)
        where  consensus_set = :consensus_set
        """,
    "sample_cons": """
        select *
        from consensus_text
        join labels using (label_id)
        join sheets using (sheet_id)
        where consensus_set = ?
        order by random()
        """,
    "traits": """
        select *
        from   traits
        join   consensus_text using (consensus_id)
        join   labels using (label_id)
        join   sheets using (sheet_id)
        where  trait_set = :trait_set
        order by consensus_id, trait_id
        """,
}
