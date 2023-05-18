import spacy
from plants.pylib.traits import (
    delete_missing,
    habit,
    link_location,
    link_part,
    link_sex,
    link_taxon_like,
    margin,
    misc,
    numeric,
    part,
    part_location,
    shape,
    surface,
    taxon,
    taxon_like,
)
from traiter.pylib.pipes import extensions, sentence, tokenizer
from traiter.pylib.traits import color, date_, elevation, geocoordinates, habitat

from .traits import admin_unit, associated_taxon, person

# from traiter.pylib.pipes import debug
# debug.tokens(nlp)  # ###########################################


def build(model_path=None):
    extensions.add_extensions()

    nlp = spacy.load("en_core_web_md", exclude=["ner"])

    tokenizer.setup_tokenizer(nlp)

    config = {"base_model": "en_core_web_md"}
    nlp.add_pipe(sentence.SENTENCES, config=config, before="parser")

    date_.build(nlp)

    misc.build(nlp)
    part.build(nlp)

    elevation.build(nlp)
    geocoordinates.build(nlp)

    color.build(nlp)
    habitat.build(nlp)

    numeric.build(nlp)
    person.build(nlp, overwrite=["subpart", "color", "count", "admin_unit"])

    habit.build(nlp)
    margin.build(nlp)
    shape.build(nlp)
    surface.build(nlp)

    admin_unit.build(nlp, overwrite=["color"])
    taxon.build(nlp, extend=2, overwrite=["habitat", "color"], auth_keep=["not_name"])

    part_location.build(nlp)
    taxon_like.build(nlp)

    link_part.build(nlp)
    link_sex.build(nlp)
    link_location.build(nlp)
    link_taxon_like.build(nlp)

    delete_missing.build(nlp)

    associated_taxon.build(nlp)

    if model_path:
        nlp.to_disk(model_path)

    return nlp


def load(model_path):
    extensions.add_extensions()
    nlp = spacy.load(model_path)
    return nlp
