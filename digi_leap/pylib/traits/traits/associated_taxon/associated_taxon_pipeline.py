from spacy import Language
from traiter.pylib.traits import add_pipe as add
from traiter.pylib.traits import trait_util

from . import associated_taxon_action as act
from . import associated_taxon_patterns as pat


def build(nlp: Language, **kwargs):

    with nlp.select_pipes(enable="tokenizer"):
        prev = add.term_pipe(
            nlp, name="assoc_taxon_terms", path=act.ASSOC_CSV, **kwargs
        )

    prev = add.trait_pipe(
        nlp,
        name="assoc_taxon_patterns",
        compiler=pat.associated_taxon_patterns(),
        after=prev,
    )
    # prev = add.debug_tokens(nlp, after=prev)  # ################################

    prev = add.cleanup_pipe(
        nlp,
        name="assoc_taxon_cleanup",
        remove=trait_util.labels_to_remove(act.ASSOC_CSV),
        after=prev,
    )

    prev = add.custom_pipe(nlp, act.LABEL_ASSOC_TAXON, after=prev)

    prev = add.cleanup_pipe(
        nlp,
        name="assoc_taxon_cleanup2",
        remove=["assoc_taxon"],
        after=prev,
    )

    return prev
