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
    "cons": """
        insert into cons ( label_id,  cons_set,  ocr_set,  cons_text)
                  values (:label_id, :cons_set, :ocr_set, :cons_text);
        """,
    "traits": """
        insert into traits ( trait_set,  cons_id,  trait,  data)
                    values (:trait_set, :cons_id, :trait, :data);
        """,
    "evals": """
        insert into evals
               ( eval_set,   sheet_id,  pred_class,  pred_conf,
                 pred_left,  pred_top,  pred_right,  pred_bottom)
        values (:eval_set,  :sheet_id, :pred_class, :pred_conf,
                :pred_left, :pred_top, :pred_right, :pred_bottom);
        """,
}

CANNED_SELECTS = {
    "labels": """
        select * from labels join sheets using (sheet_id)
        where label_set = :label_set;
        """,
    "label_split": """
        select * from sheets left join labels using (sheet_id)
        where split = :split and label_set = :label_set;
        """,
    "ocr": """
        select * from ocr join labels using (label_id) join sheets using (sheet_id)
        where ocr_set = :ocr_set;
        """,
    "cons": """
        select * from cons join labels using (label_id) join sheets using (sheet_id)
        where cons_set = :cons_set
        """,
    "sample_cons": """
        select * from cons join labels using (label_id) join sheets using (sheet_id)
        where cons_set = ?
        order by random()
        """,
    "traits": """
        select *
        from traits
        join cons using (cons_id)
        join labels using (label_id)
        join sheets using (sheet_id)
        where trait_set = :trait_set
        order by cons_id, trait_id
        """,
}
