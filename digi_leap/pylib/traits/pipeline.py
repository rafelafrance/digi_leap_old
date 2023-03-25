from plants.pylib import const as p_const
from plants.pylib.patterns import deletes
from traiter.pylib.term_list import TermList

from .pipeline_builder import PipelineBuilder


def pipeline():
    pipes = PipelineBuilder(base_model="en_core_web_md")

    pipes.traits_without_matcher = p_const.TRAITS_WITHOUT_MATCHER

    pipes.tokenizer()

    # Before the spacy NER (Name Entity Recognition) pipe
    pipes.taxon_terms(before="ner")
    pipes.taxa(n=2, before="ner")
    pipes.taxa_like()

    pipes.plant_terms(before="ner")

    pipes.dates(merge=True, before="ner")
    pipes.elevations(before="ner")
    pipes.habitats(before="ner")
    pipes.lat_longs(before="ner")

    pipes.parts(before="ner")
    pipes.sex(before="ner")
    pipes.numerics(before="ner")
    pipes.shapes(before="ner")
    pipes.margins(before="ner")
    pipes.colors(before="ner")
    pipes.part_location(before="ner")

    labels = TermList().read(p_const.VOCAB_DIR / "job_labels.csv").labels()
    labels += ["no_label"]
    pipes.delete_traits("delete_partials", keep=labels, keep_outputs=True, before="ner")

    pipes.link_parts(before="ner")
    pipes.link_parts_once(before="ner")
    pipes.link_subparts(before="ner")
    pipes.link_subparts_suffixes(before="ner")
    pipes.link_sex(before="ner")
    pipes.link_locations(before="ner")
    pipes.link_taxa_like(before="ner")

    delete_when = {
        "count": [deletes.DELETE_MISSING_PARTS, deletes.DELETE_PAGE_NO],
        "count_group": deletes.DELETE_MISSING_PARTS,
        "count_suffix": deletes.DELETE_MISSING_COUNT,
        "part": deletes.DELETE_OTHERS,
        "size": [deletes.DELETE_MISSING_PARTS, deletes.DELETE_KM],
    }
    pipes.delete_traits("delete_numerics", delete_when=delete_when, before="ner")

    # After the spacy NER (Name Entity Recognition) pipe
    # Leveraging spacy's PERSON entities from the built-in NER pipe to parse names
    pipes.names()
    pipes.jobs()
    pipes.delete_traits("delete_names", delete=["name", "PERSON"])

    pipes.admin_unit_terms()
    pipes.admin_unit()

    pipes.associated_taxon()

    pipes.delete_traits("final_delete", keep_outputs=True)

    # pipes.debug_tokens(before="ner")  # ############################################
    # pipes.debug_tokens()  # ############################################

    return pipes.build()
