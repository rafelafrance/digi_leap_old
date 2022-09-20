CANNED_INSERTS = {
    "char_sub_matrix": """
        insert into char_sub_matrix
               ( char1,  char2,  char_set,  score,  sub)
        values (:char1, :char2, :char_set, :score, :sub);
        """,
    "consensuses": """
        insert into consensuses
                         ( label_id,  consensus_set,  ocr_set,  consensus_text)
                  values (:label_id, :consensus_set, :ocr_set, :consensus_text);
        """,
    "label_finder_tests": """
        insert into label_finder_tests
               ( train_set,   sheet_id,  train_class,  pred_conf,
                 train_left,  train_top,  train_right,  train_bottom)
        values (:train_set,  :sheet_id, :train_class, :pred_conf,
                :train_left, :train_top, :train_right, :train_bottom);
        """,
    "label_finder_train": """
        insert into label_finder_train
               ( train_set,   sheet_id,  train_class,
                 train_left,  train_top,  train_right,  train_bottom)
        values (:train_set,  :sheet_id, :train_class,
                :train_left, :train_top, :train_right, :train_bottom);
        """,
    "labels": """
        insert into labels
               ( sheet_id,    label_set,  class,  label_conf,
                 label_left,  label_top,  label_right,  label_bottom)
        values (:sheet_id,   :label_set, :class, :label_conf,
                :label_left, :label_top, :label_right, :label_bottom);
        """,
    "ocr_scores": """
        insert into ocr_scores
               ( score_set,   label_id,  gold_id,  gold_set,  pipeline,
                 score_text,  score)
        values (:score_set,  :label_id, :gold_id, :gold_set, :pipeline,
                :score_text, :score)
        """,
    "ocr_texts": """
        insert into ocr_texts
               ( label_id,  ocr_set,  pipeline,  ocr_text)
        values (:label_id, :ocr_set, :pipeline, :ocr_text);
        """,
    "sheets": """
        insert into sheets
               ( sheet_set,  path,  width,  height,  coreid,  split)
        values (:sheet_set, :path, :width, :height, :coreid, :split);
        """,
    "traits": """
        insert into traits ( trait_set,  consensus_id,  trait,  data)
                    values (:trait_set, :consensus_id, :trait, :data);
        """,
}

CANNED_SELECTS = {
    "consensuses": """
        select *
        from   consensuses
        join   labels using (label_id)
        join   sheets using (sheet_id)
        where  consensus_set = :consensus_set
        """,
    "labels": """
        select *
        from   labels
        join   sheets using (sheet_id)
        where  label_set = :label_set
        and    label_conf >= :label_conf
        """,
    "ocr_texts": """
        select *
        from   ocr_texts
        join   labels using (label_id)
        join   sheets using (sheet_id)
        where  ocr_set = :ocr_set
        """,
    "sample_consensuses": """
        select *
        from consensuses
        join labels using (label_id)
        join sheets using (sheet_id)
        where consensus_set = :consensus_set
        order by random()
        """,
    "train_labels": """
        select *
        from   label_finder_train
        join   sheets using (sheet_id)
        where  split = :split
        and    train_set = :train_set
        order by sheet_id
        """,
    "train_split": """
        select    *
        from      sheets
        left join label_finder_train using (sheet_id)
        where     split = :split
        and       train_set = :train_set
        """,
    "traits": """
        select *
        from   traits
        join   consensuses using (consensus_id)
        join   labels using (label_id)
        join   sheets using (sheet_id)
        where  trait_set = :trait_set
        order by consensus_id, trait_id
        """,
}


CANNED_DELETES = {}
