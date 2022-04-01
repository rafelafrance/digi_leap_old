"""Common pipeline functions & constants."""
import os
import string
from pathlib import Path

from traiter import tokenizer_util
from traiter.pipes.cleanup import CLEANUP
from traiter.pipes.debug import DEBUG_ENTITIES
from traiter.pipes.debug import DEBUG_TOKENS

from ..patterns import forget_patterns


# ##########################################################################
# Vocabulary locations
class Dir:
    """File locations."""

    curr_dir = Path(os.getcwd())
    is_subdir = curr_dir.name in ("notebooks", "experiments")
    root_dir = Path(".." if is_subdir else ".")
    vocab_dir = root_dir / "digi_leap" / "pylib" / "trait_extractor" / "vocabulary"


# ##########################################################################
def infix():
    """Adjust how the tokenizer splits words."""
    return [
        r"(?<=[0-9])[/,](?=[0-9])",  # digit,digit
        r"(?<=[A-Z])[/-](?=[0-9])",  # letter-digit
        "-_",
    ]


# #########################################################################
def abbreviations():
    """Get abbreviations for the term tokenizer."""
    abbrevs = """
        Jan. Feb. Febr. Mar. Apr. Jun. Jul. Aug. Sep. Sept. Oct. Nov. Dec.
        Acad. Amer. Ann. Arq. Bol. Bot. Bull. Cat. Coll. Com. Contr. Exot. FIG.
        Gard. Gen. Geo. Herb. Hort. Hist. Is. Jahrb. Jr. Lab. Leg. Legum. Linn.
        Mem. Mex. Mts. Mus. Nac. Nat. Neg. No. Ocas. Proc. Prodr. Prov. Pto. Publ.
        Sci. Soc. Spec. Ser. Spp. Sr. Sta. Sto. Sul. Suppl. Syst.
        Tex. Trans. Univ. US. U.S. Veg. Wm.
        adj. al. alt. ann. bot. bras. ca. cent. centr. cf. coll. depto. diam. dtto.
        ed. ememd. ent. est.
        fig. figs. fl. flor. flumin. gard. hb. hist. illeg. infra. is. jug.
        lam. lat. leg. lin. long. mem. mens. monac. mont. mun.
        nat. no. nom. nud. p. pi. pr. prov. reg.
        s. sci. spp. stat. stk. str. superfl. suppl. surv. syn. telegr. veg.
        i. ii. iii. iv. v. vi. vii. viii. ix. x. xi. xii. xiii. xiv. xv. xvi. xvii.
        xviii. xix. xx. xxi. xxii. xxiii. xxiv. xxv.
        I. II. III. IV. V. VI. VII. VIII. IX. X. XI. XII. XIII. XIV. XV. XVI. XVII.
        XVIII. XIX. XX. XXI. XXII. XXIII. XXIV. XXV.
        m. var. sect. subsect. ser. subser. subsp. sp. nov.
        """.split()
    abbrevs += [f"{c}." for c in string.ascii_uppercase]
    return abbrevs


# #########################################################################
def setup_term_pipe(nlp, terms):
    """Setup terms"""
    tokenizer_util.append_prefix_regex(nlp)
    tokenizer_util.append_infix_regex(nlp, infix())
    tokenizer_util.append_suffix_regex(nlp)
    tokenizer_util.append_abbrevs(nlp, abbreviations())

    term_ruler = nlp.add_pipe(
        "entity_ruler",
        name="term_ruler",
        before="parser",
        config={"phrase_matcher_attr": "LOWER"},
    )
    term_ruler.add_patterns(terms.for_entity_ruler())


def debug_tokens(nlp, name=None, after=None):
    """Add a pipe to see the current tokens."""
    nlp.add_pipe(DEBUG_TOKENS, name=name, after=after)


def debug_entities(nlp, name=None, after=None):
    """Add a pipe to see the current tokens."""
    nlp.add_pipe(DEBUG_ENTITIES, name=name, after=after)


def forget_entities(nlp, forget=None, name=None, after=None):
    """Remove dangling entities."""
    forget = forget if forget else forget_patterns.all_entities()
    nlp.add_pipe(CLEANUP, name=name, after=after, config={"forget": forget})