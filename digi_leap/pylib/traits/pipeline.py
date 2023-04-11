import spacy
from plants.pylib.traits.delete_missing import delete_missing_pipeline
from plants.pylib.traits.habit import habit_pipeline
from plants.pylib.traits.link_location import link_location_pipeline
from plants.pylib.traits.link_part import link_part_pipeline
from plants.pylib.traits.link_sex import link_sex_pipeline
from plants.pylib.traits.link_taxon_like import link_taxon_like_pipeline
from plants.pylib.traits.margin import margin_pipeline
from plants.pylib.traits.misc import misc_pipeline
from plants.pylib.traits.numeric import numeric_pipeline
from plants.pylib.traits.part import part_pipeline
from plants.pylib.traits.part_location import part_location_pipeline
from plants.pylib.traits.shape import shape_pipeline
from plants.pylib.traits.surface import surface_pipeline
from plants.pylib.traits.taxon import taxon_pipeline
from plants.pylib.traits.taxon_like import taxon_like_pipeline
from traiter.pylib import tokenizer
from traiter.pylib.pipes import extensions
from traiter.pylib.traits.color import color_pipeline
from traiter.pylib.traits.date import date_pipeline
from traiter.pylib.traits.elevation import elevation_pipeline
from traiter.pylib.traits.habitat import habitat_pipeline
from traiter.pylib.traits.lat_long import lat_long_pipeline
from traits.admin_unit import admin_unit_pipeline
from traits.associated_taxon import associated_taxon_pipeline
from traits.person import person_pipeline


def build(model_path=None):
    extensions.add_extensions()

    nlp = spacy.load("en_core_web_md", exclude=["parser"])

    tokenizer.setup_tokenizer(nlp)

    # Locate as many traits as possible before we use spacy's NER pipe

    taxon_pipeline.build(nlp, extend=2, before="ner")

    misc_pipeline.build(nlp, before="ner")
    part_pipeline.build(nlp, before="ner")
    numeric_pipeline.build(nlp, before="ner")

    color_pipeline.build(nlp, before="ner")
    date_pipeline.build(nlp, before="ner")
    elevation_pipeline.build(nlp, before="ner")
    habitat_pipeline.build(nlp, before="ner")
    lat_long_pipeline.build(nlp, before="ner")

    habit_pipeline.build(nlp, before="ner")
    margin_pipeline.build(nlp, before="ner")
    shape_pipeline.build(nlp, before="ner")
    surface_pipeline.build(nlp, before="ner")

    part_location_pipeline.build(nlp, before="ner")
    taxon_like_pipeline.build(nlp, before="ner")

    link_part_pipeline.build(nlp, before="ner")
    link_sex_pipeline.build(nlp, before="ner")
    link_location_pipeline.build(nlp, before="ner")
    link_taxon_like_pipeline.build(nlp, before="ner")

    delete_missing_pipeline.build(nlp, before="ner")

    associated_taxon_pipeline.build(nlp, before="ner")

    # Leveraging spacy's PERSON entities from the built-in NER pipe to parse names

    person_pipeline.build(nlp)
    admin_unit_pipeline.build(nlp)

    if model_path:
        nlp.to_disk(model_path)

    # for name in nlp.pipe_names:
    #     print(name)

    return nlp
