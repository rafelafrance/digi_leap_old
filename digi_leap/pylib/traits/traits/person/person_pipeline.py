from spacy.language import Language
from traiter.pylib.traits import add_pipe as add

from . import person_action as act
from . import person_patterns as pat


def build(nlp: Language, **kwargs):

    with nlp.select_pipes(enable="tokenizer"):
        prev = add.term_pipe(nlp, name="person_terms", path=act.ALL_CSVS, **kwargs)

    prev = add.trait_pipe(
        nlp,
        name="name_patterns",
        compiler=pat.name_patterns(),
        overwrite=["name_prefix", "name_suffix", "color", "no_label", "count"],
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

    prev = add.cleanup_pipe(nlp, name="person_cleanup", after=prev)

    return prev
