from spacy import Language
from traiter.traits import add_pipe as add
from traiter.traits import trait_util

from . import admin_unit_action as act
from . import admin_unit_patterns as pat


def build(nlp: Language, **kwargs):

    with nlp.select_pipes(enable="tokenizer"):
        prev = add.term_pipe(nlp, name="admin_unit_terms", path=act.ALL_CSVS, **kwargs)

    prev = add.trait_pipe(
        nlp,
        name="not_admin_unit",
        compiler=pat.not_admin_unit(),
        after=prev,
    )

    prev = add.trait_pipe(
        nlp,
        name="admin_unit_patterns",
        compiler=pat.admin_unit_patterns(),
        after=prev,
    )

    # prev = add.debug_tokens(nlp, after=prev)  # ################################

    prev = add.cleanup_pipe(
        nlp,
        name="admin_unit_cleanup",
        remove=trait_util.labels_to_remove(act.ALL_CSVS, keep=["admin_unit"]),
        after=prev,
    )

    return prev
