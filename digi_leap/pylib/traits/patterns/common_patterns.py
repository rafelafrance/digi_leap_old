from traiter.pylib import const as t_const

PATTERNS = {
    ":": {"TEXT": {"IN": t_const.COLON}},
    ",": {"TEXT": {"IN": t_const.COMMA}},
    ".": {"TEXT": {"IN": t_const.DOT}},
    "(": {"TEXT": {"IN": t_const.OPEN}},
    ")": {"TEXT": {"IN": t_const.CLOSE}},
}
