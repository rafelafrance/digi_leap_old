"""Terms common to all pipelines."""
from traiter import const as t_const

COMMON_PATTERNS = {
    ":": {"TEXT": {"IN": t_const.COLON}},
    ",": {"TEXT": {"IN": t_const.COMMA}},
}
