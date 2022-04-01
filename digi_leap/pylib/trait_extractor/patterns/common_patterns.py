"""Terms common to all pipelines."""
from traiter import const as t_const


def get_common_patterns():
    """These patterns get used in several places."""
    return {
        ":": {"TEXT": {"IN": t_const.COLON}},
        ",": {"TEXT": {"IN": t_const.COMMA}},
    }