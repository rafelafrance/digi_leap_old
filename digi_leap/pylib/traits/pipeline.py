from plants.pylib import const as p_const
from plants.pylib.patterns import deletes
from traiter.pylib.term_list import TermList

from .pipeline_builder import PipelineBuilder


def pipeline():
    pipes = PipelineBuilder(base_model="en_core_web_md")

    pipes.tokenizer()

    # Happens before the spacy NER (Name Entity Recognition) pipe
    pipes.taxon_terms(before="ner")
    pipes.taxa(n=2, before="ner")
    pipes.taxa_like()

    pipes.plant_terms(before="ner")

    pipes.parts(before="ner")
    pipes.sex(before="ner")
    pipes.numerics(before="ner")
    pipes.shapes(before="ner")
    pipes.margins(before="ner")
    pipes.colors(before="ner")
    pipes.part_location(before="ner")

    pipes.dates(merge=True, before="ner")
    pipes.elevations(before="ner")
    pipes.habitats(before="ner")
    pipes.lat_longs(before="ner")

    labels = TermList().read(p_const.VOCAB_DIR / "job_labels.csv").labels()
    labels += ["no_label"]
    pipes.delete_traits("delete_partials", keep_outputs=labels, before="ner")

    pipes.link_parts(before="ner")
    pipes.link_parts_once(before="ner")
    pipes.link_subparts(before="ner")
    pipes.link_subparts_suffixes(before="ner")
    pipes.link_sex(before="ner")
    pipes.link_locations(before="ner")
    pipes.link_taxa_like(before="ner")

    pipes.delete_traits(
        "delete_unlinked", delete_when=deletes.DELETE_WHEN, before="ner"
    )

    # Happens after the spacy NER (Name Entity Recognition) pipe
    # Leveraging spacy's PERSON entities built in the NER pipe to parse names
    pipes.names()
    pipes.jobs()
    pipes.delete_traits("delete_names", delete=["name", "PERSON"])

    pipes.admin_unit_terms()
    pipes.admin_unit()

    pipes.associated_taxon()

    pipes.delete_traits("final_delete", keep_outputs=True)

    # pipes.debug_tokens()  # ##############################################
    # pipes.debug_ents()  # ##############################@@################

    return pipes.build()
