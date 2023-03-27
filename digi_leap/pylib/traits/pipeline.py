from plants.pylib.patterns import deletes
from plants.pylib.vocabulary import terms as p_terms
from traiter.pylib.term_list import TermList

from .pipeline_builder import PipelineBuilder


def pipeline():
    # Because we are using spacy's NER pipe we need the bigger spacy model
    pipes = PipelineBuilder(base_model="en_core_web_md")

    pipes.traits_without_matcher = p_terms.TRAITS_WITHOUT_MATCHER

    pipes.tokenizer()

    # Before the spacy NER (Name Entity Recognition) pipe
    pipes.taxon_terms(before="ner")
    pipes.taxa(n=2, before="ner")
    pipes.taxa_like()

    terms = p_terms.PLANT_TERMS.shared("colors habitats lat_long")
    pipes.add_terms(terms, name="plant_terms", before="ner")

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

    labels = TermList().read(p_terms.VOCAB_DIR / "job_labels.csv").labels()
    labels += ["no_label"]
    pipes.delete_traits("delete_partials", keep=labels, keep_outputs=True, before="ner")

    pipes.link_parts(before="ner")
    pipes.link_parts_once(before="ner")
    pipes.link_subparts(before="ner")
    pipes.link_subparts_suffixes(before="ner")
    pipes.link_sex(before="ner")
    pipes.link_locations(before="ner")
    pipes.link_taxa_like(before="ner")

    pipes.delete_traits("delete_rules", delete_when=deletes.DELETE_WHEN, before="ner")

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
