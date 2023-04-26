from spacy.language import Language
from traiter.pylib.traits import add_pipe as add
from traiter.pylib.traits import trait_util

from . import person_action as act
from . import person_patterns as pat


def build(nlp: Language, **kwargs):

    with nlp.select_pipes(enable="tokenizer"):
        prev = add.term_pipe(nlp, name="person_terms", path=act.ALL_CSVS, **kwargs)

    prev = add.trait_pipe(
        nlp,
        name="name_patterns",
        compiler=pat.name_patterns(),
        keep=["date"],
        overwrite=["name_prefix", "name_suffix", "color", "no_label"],
        after=prev,
    )

    overwrite = """
        name col_label det_label no_label other_label subpart id_no
        """.split()
    prev = add.trait_pipe(
        nlp,
        name="job_patterns",
        compiler=pat.job_patterns(),
        overwrite=overwrite,
        after=prev,
    )

    prev = add.trait_pipe(
        nlp,
        name="other_collector_patterns",
        compiler=pat.other_collector_patterns(),
        overwrite=["other_collector"],
        after=prev,
    )
    # prev = add.debug_tokens(nlp, after=prev)  # #############################

    keep = ["collector", "determiner", "other_collector"]
    remove = trait_util.labels_to_remove(act.ALL_CSVS, keep=keep)
    remove += ["name", "not_name", "not_collector", "id_no"]
    prev = add.cleanup_pipe(nlp, name="person_cleanup", remove=remove, after=prev)

    return prev
