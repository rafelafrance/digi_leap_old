import spacy
from plants.traits.delete_missing import delete_missing_pipeline
from plants.traits.habit import habit_pipeline
from plants.traits.link_location import link_location_pipeline
from plants.traits.link_part import link_part_pipeline
from plants.traits.link_sex import link_sex_pipeline
from plants.traits.link_taxon_like import link_taxon_like_pipeline
from plants.traits.margin import margin_pipeline
from plants.traits.misc import misc_pipeline
from plants.traits.numeric import numeric_pipeline
from plants.traits.part import part_pipeline
from plants.traits.part_location import part_location_pipeline
from plants.traits.shape import shape_pipeline
from plants.traits.surface import surface_pipeline
from plants.traits.taxon import taxon_pipeline
from plants.traits.taxon_like import taxon_like_pipeline
from traiter.pipes import extensions
from traiter.pipes import tokenizer
from traiter.traits.color import color_pipeline
from traiter.traits.date import date_pipeline
from traiter.traits.elevation import elevation_pipeline
from traiter.traits.habitat import habitat_pipeline
from traiter.traits.lat_long import lat_long_pipeline

from .traits.admin_unit import admin_unit_pipeline
from .traits.associated_taxon import associated_taxon_pipeline
from .traits.person import person_pipeline


def build(model_path=None):
    extensions.add_extensions()

    nlp = spacy.load("en_core_web_md", exclude=["ner", "parser"])

    tokenizer.setup_tokenizer(nlp)

    taxon_pipeline.build(nlp, extend=2)

    misc_pipeline.build(nlp)
    part_pipeline.build(nlp)
    numeric_pipeline.build(nlp)

    color_pipeline.build(nlp)
    date_pipeline.build(nlp)
    elevation_pipeline.build(nlp)
    habitat_pipeline.build(nlp)
    lat_long_pipeline.build(nlp)

    habit_pipeline.build(nlp)
    margin_pipeline.build(nlp)
    shape_pipeline.build(nlp)
    surface_pipeline.build(nlp)

    part_location_pipeline.build(nlp)
    taxon_like_pipeline.build(nlp)

    link_part_pipeline.build(nlp)
    link_sex_pipeline.build(nlp)
    link_location_pipeline.build(nlp)
    link_taxon_like_pipeline.build(nlp)

    delete_missing_pipeline.build(nlp)

    associated_taxon_pipeline.build(nlp)

    admin_unit_pipeline.build(nlp)

    person_pipeline.build(nlp)

    if model_path:
        nlp.to_disk(model_path)

    # for name in nlp.pipe_names:

    return nlp
