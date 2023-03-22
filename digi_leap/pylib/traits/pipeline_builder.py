from plants.pylib import pipeline_builder as p_builder

from .patterns import admin_unit
from .patterns import associated_taxon
from .patterns import collector
from .patterns import determiner
from .patterns import name
from .patterns import terms


class PipelineBuilder(p_builder.PipelineBuilder):
    def treatment_terms(self, **kwargs):
        return self.add_terms(
            terms.TREATMENT_TERMS,
            name="treatment_terms",
            replace=terms.TREATMENT_TERMS.pattern_dict("replace"),
            merge=True,
            **kwargs,
        )

    def names(self, **kwargs) -> str:
        labels = [lb for lb in self.spacy_ent_labels if lb != "PERSON"]
        self.delete_traits(name="delete_spacy", delete=labels, **kwargs)
        return self.add_traits(
            [name.NAME, name.NOT_NAME], name="names", after="delete_spacy"
        )

    def jobs(self, **kwargs) -> str:
        return self.add_traits(
            [collector.COLLECTOR, collector.NOT_COLLECTOR, determiner.DETERMINER],
            name="jobs",
            **kwargs,
        )

    def associated_taxa(self, **kwargs) -> str:
        prev = self.add_traits(
            [associated_taxon.ASSOC_TAXA], name="associated_taxa", **kwargs
        )

        name_ = "primary_taxa"
        self.nlp.add_pipe(
            associated_taxon.PRIMARY_TAXON, name=name_, after=prev, **kwargs
        )
        return name_

    def admin_unit_terms(self, **kwargs) -> str:
        return self.add_terms(
            terms.ADMIN_UNIT_TERMS, name="admin_terms", merge=True, **kwargs
        )

    def admin_units(self, **kwargs) -> str:
        prev = self.add_traits(
            [admin_unit.NOT_COUNTY],
            name="not_admin_units",
            **kwargs,
        )
        return self.add_traits(
            [
                admin_unit.COUNTY_STATE,
                admin_unit.COUNTY_STATE_IFFY,
                admin_unit.COUNTY_ONLY,
                admin_unit.STATE_COUNTY,
                admin_unit.STATE_ONLY,
            ],
            name="admin_units",
            after=prev,
            **kwargs,
        )
