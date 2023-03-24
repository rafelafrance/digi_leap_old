from plants.pylib import pipeline_builder as p_builder
from traiter.pylib import pipeline_builder as t_builder

from .. import const
from .patterns import admin_units
from .patterns import associated_taxa
from .patterns import collectors
from .patterns import determiners
from .patterns import names


class PipelineBuilder(p_builder.PipelineBuilder):
    def _primary_taxa(self, *, name, **kwargs):
        self.nlp.add_pipe(associated_taxa.PRIMARY_TAXON, name=name, **kwargs)

    def names(self, **kwargs) -> str:
        labels = [lb for lb in self.spacy_ent_labels if lb != "PERSON"]
        self.delete_traits(name="delete_spacy", delete=labels, **kwargs)
        return self.add_traits(
            [names.NAME, names.NOT_NAME], name="names", after="delete_spacy"
        )

    def jobs(self, **kwargs) -> str:
        return self.add_traits(
            [collectors.COLLECTOR, collectors.NOT_COLLECTOR, determiners.DETERMINER],
            name="jobs",
            **kwargs,
        )

    def associated_taxon(self, **kwargs) -> str:
        prev = self.add_traits(
            [associated_taxa.ASSOC_TAXA], name="associated_taxa", **kwargs
        )

        name = "primary_taxa"
        kwargs = {"name": name, "after": prev}
        self.pipeline.append(t_builder.Pipe(self._primary_taxa, kwargs))
        return name

    def admin_unit_terms(self, **kwargs) -> str:
        return self.add_terms(
            const.ADMIN_UNIT_TERMS, name="admin_terms", merge=True, **kwargs
        )

    def admin_unit(self, **kwargs) -> str:
        prev = self.add_traits(
            [admin_units.NOT_COUNTY],
            name="not_admin_units",
            **kwargs,
        )
        return self.add_traits(
            [
                admin_units.COUNTY_STATE,
                admin_units.COUNTY_STATE_IFFY,
                admin_units.COUNTY_ONLY,
                admin_units.STATE_COUNTY,
                admin_units.STATE_ONLY,
            ],
            name="admin_units",
            after=prev,
        )
