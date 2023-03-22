from plants.pylib.patterns import delete

from .patterns import terms
from .pipeline_builder import PipelineBuilder


def pipeline():
    pipes = PipelineBuilder(base_model="en_core_web_md")

    pipes.tokenizer()

    # Happens before the spacy NER (Name Entity Recognition) pipe
    pipes.taxon_terms(before="ner")
    pipes.taxa(n=2, before="ner")
    pipes.taxa_like()

    pipes.treatment_terms(before="ner")

    pipes.parts(before="ner")
    pipes.sex(before="ner")
    pipes.numerics(before="ner")
    pipes.shapes(before="ner")
    pipes.margins(before="ner")
    pipes.colors(before="ner")
    pipes.part_locations(before="ner")

    pipes.dates(before="ner")
    pipes.elevations(before="ner")
    pipes.habitats(before="ner")
    pipes.lat_longs(before="ner")

    keep = terms.KEEP + ["col_label", "det_label", "no_label"]
    pipes.delete_traits("delete_partials", keep=keep, before="ner")

    pipes.link_parts(before="ner")
    pipes.link_parts_once(before="ner")
    pipes.link_subparts(before="ner")
    pipes.link_subparts_suffixes(before="ner")
    pipes.link_sex(before="ner")
    pipes.link_locations(before="ner")
    pipes.link_taxa_like(before="ner")

    pipes.delete_traits("delete_unlinked", delete_when=delete.DELETE_WHEN, before="ner")

    # Happens after the spacy NER (Name Entity Recognition) pipe
    # Leveraging spacy's PERSON entities to parse names
    pipes.names()
    pipes.jobs()
    pipes.delete_traits("delete_names", delete=["name", "PERSON"])

    # pipes.debug_tokens()  # #####################################################
    pipes.admin_unit_terms()
    pipes.admin_units()

    # Happens after the spacy NER (Name Entity Recognition) pipe
    pipes.associated_taxa()

    pipes.delete_traits("final_delete", keep=terms.KEEP)

    return pipes
