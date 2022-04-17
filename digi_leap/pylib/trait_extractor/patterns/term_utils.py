"""Term patterns."""
import string

from traiter import tokenizer_util
from traiter.terms.db import Db

from ...consts import DATA_DIR
from ...consts import MOCK_DIR


# ##########################################################################
TERM_DB = DATA_DIR / "terms.sqlite"
if not TERM_DB.exists():
    TERM_DB = MOCK_DIR / "terms.sqlite"

# ##########################################################################
EXTRACTOR_TERMS = Db()
EXTRACTOR_TERMS += Db.shared("time")
EXTRACTOR_TERMS += Db.select_term_set(TERM_DB, "jobs")

# ##########################################################################
VOCAB_TERMS = Db()
VOCAB_TERMS += Db.shared("us_locations taxon_levels")
VOCAB_TERMS += Db.select_term_set(TERM_DB, "plant_taxa")

REPLACE = VOCAB_TERMS.pattern_dict("replace")

COUNTY_IN = VOCAB_TERMS.pattern_dict("inside")
POSTAL = VOCAB_TERMS.pattern_dict("postal")

LEVEL = VOCAB_TERMS.pattern_dict("level")
LEVEL = {k: v.split() for k, v in LEVEL.items()}

# #########################################################################
ABBREVS = """
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
ABBREVS += [f"{c}." for c in string.ascii_uppercase]

INFIX = [
    r"(?<=[0-9])[/,](?=[0-9])",  # digit,digit
    r"(?<=[A-Z])[/-](?=[0-9])",  # letter-digit
    "-_",
]


def setup_tokenizer(nlp):
    tokenizer_util.remove_special_case(nlp, EXTRACTOR_TERMS.terms)
    tokenizer_util.remove_special_case(nlp, VOCAB_TERMS.terms)
    tokenizer_util.append_prefix_regex(nlp)
    tokenizer_util.append_infix_regex(nlp, INFIX)
    tokenizer_util.append_suffix_regex(nlp)
    tokenizer_util.append_abbrevs(nlp, ABBREVS)
