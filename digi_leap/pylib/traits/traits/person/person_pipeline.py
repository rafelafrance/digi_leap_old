from spacy import Language
from traiter.pylib.traits import add_pipe as add
from traiter.pylib.traits import trait_util

from . import person_action as act
from . import person_patterns as pat


def build(nlp: Language, **kwargs):

    with nlp.select_pipes(enable="tokenizer"):
        prev = add.term_pipe(nlp, name="person_terms", path=act.ALL_CSVS, **kwargs)

    # prev = add.debug_tokens(nlp, after=prev)  # ################################

    # We only want the PERSON label from spacy's NER pipe
    labels = [lb for lb in nlp.meta["labels"].get("ner", []) if lb != "PERSON"]
    prev = add.cleanup_pipe(nlp, name="spacy_cleanup", remove=labels, after=prev)

    prev = add.trait_pipe(
        nlp,
        name="person_name_patterns",
        compiler=pat.person_name_patterns(),
        after=prev,
    )

    prev = add.trait_pipe(
        nlp,
        name="person_job_patterns",
        compiler=pat.job_patterns(),
        after=prev,
    )

    keep = ["collector", "determiner"]
    remove = trait_util.labels_to_remove(act.ALL_CSVS, keep=keep) + ["PERSON", "name"]
    prev = add.cleanup_pipe(nlp, name="person_cleanup", remove=remove, after=prev)

    return prev
