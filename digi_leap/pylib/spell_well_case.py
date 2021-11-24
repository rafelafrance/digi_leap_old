"""The to lower case mappings for C++."""


_TO_LOWER = [
    # Upper code point, lower code point
    ("\u0041", "\u0061"),
    ("\u0042", "\u0062"),
    ("\u0043", "\u0063"),
    ("\u0044", "\u0064"),
    ("\u0045", "\u0065"),
    ("\u0046", "\u0066"),
    ("\u0047", "\u0067"),
    ("\u0048", "\u0068"),
    ("\u0049", "\u0069"),
    ("\u004A", "\u006A"),
    ("\u004B", "\u006B"),
    ("\u004C", "\u006C"),
    ("\u004D", "\u006D"),
    ("\u004E", "\u006E"),
    ("\u004F", "\u006F"),
    ("\u0050", "\u0070"),
    ("\u0051", "\u0071"),
    ("\u0052", "\u0072"),
    ("\u0053", "\u0073"),
    ("\u0054", "\u0074"),
    ("\u0055", "\u0075"),
    ("\u0056", "\u0076"),
    ("\u0057", "\u0077"),
    ("\u0058", "\u0078"),
    ("\u0059", "\u0079"),
    ("\u005A", "\u007A"),
    ("\u00C0", "\u00E0"),
    ("\u00C1", "\u00E1"),
    ("\u00C2", "\u00E2"),
    ("\u00C3", "\u00E3"),
    ("\u00C4", "\u00E4"),
    ("\u00C5", "\u00E5"),
    ("\u00C6", "\u00E6"),
    ("\u00C7", "\u00E7"),
    ("\u00C8", "\u00E8"),
    ("\u00C9", "\u00E9"),
    ("\u00CA", "\u00EA"),
    ("\u00CB", "\u00EB"),
    ("\u00CC", "\u00EC"),
    ("\u00CD", "\u00ED"),
    ("\u00CE", "\u00EE"),
    ("\u00CF", "\u00EF"),
    ("\u00D0", "\u00F0"),
    ("\u00D1", "\u00F1"),
    ("\u00D2", "\u00F2"),
    ("\u00D3", "\u00F3"),
    ("\u00D4", "\u00F4"),
    ("\u00D5", "\u00F5"),
    ("\u00D6", "\u00F6"),
    ("\u00D8", "\u00F8"),
    ("\u00D9", "\u00F9"),
    ("\u00DA", "\u00FA"),
    ("\u00DB", "\u00FB"),
    ("\u00DC", "\u00FC"),
    ("\u00DD", "\u00FD"),
    ("\u00DE", "\u00FE"),
    ("\u0100", "\u0101"),
    ("\u0102", "\u0103"),
    ("\u0104", "\u0105"),
    ("\u0106", "\u0107"),
    ("\u0108", "\u0109"),
    ("\u010A", "\u010B"),
    ("\u010C", "\u010D"),
    ("\u010E", "\u010F"),
    ("\u0110", "\u0111"),
    ("\u0112", "\u0113"),
    ("\u0114", "\u0115"),
    ("\u0116", "\u0117"),
    ("\u0118", "\u0119"),
    ("\u011A", "\u011B"),
    ("\u011C", "\u011D"),
    ("\u011E", "\u011F"),
    ("\u0120", "\u0121"),
    ("\u0122", "\u0123"),
    ("\u0124", "\u0125"),
    ("\u0126", "\u0127"),
    ("\u0128", "\u0129"),
    ("\u012A", "\u012B"),
    ("\u012C", "\u012D"),
    ("\u012E", "\u012F"),
    ("\u0130", "\u0069"),
    ("\u0132", "\u0133"),
    ("\u0134", "\u0135"),
    ("\u0136", "\u0137"),
    ("\u0139", "\u013A"),
    ("\u013B", "\u013C"),
    ("\u013D", "\u013E"),
    ("\u013F", "\u0140"),
    ("\u0141", "\u0142"),
    ("\u0143", "\u0144"),
    ("\u0145", "\u0146"),
    ("\u0147", "\u0148"),
    ("\u014A", "\u014B"),
    ("\u014C", "\u014D"),
    ("\u014E", "\u014F"),
    ("\u0150", "\u0151"),
    ("\u0152", "\u0153"),
    ("\u0154", "\u0155"),
    ("\u0156", "\u0157"),
    ("\u0158", "\u0159"),
    ("\u015A", "\u015B"),
    ("\u015C", "\u015D"),
    ("\u015E", "\u015F"),
    ("\u0160", "\u0161"),
    ("\u0162", "\u0163"),
    ("\u0164", "\u0165"),
    ("\u0166", "\u0167"),
    ("\u0168", "\u0169"),
    ("\u016A", "\u016B"),
    ("\u016C", "\u016D"),
    ("\u016E", "\u016F"),
    ("\u0170", "\u0171"),
    ("\u0172", "\u0173"),
    ("\u0174", "\u0175"),
    ("\u0176", "\u0177"),
    ("\u0178", "\u00FF"),
    ("\u0179", "\u017A"),
    ("\u017B", "\u017C"),
    ("\u017D", "\u017E"),
    ("\u0181", "\u0253"),
    ("\u0182", "\u0183"),
    ("\u0184", "\u0185"),
    ("\u0186", "\u0254"),
    ("\u0187", "\u0188"),
    ("\u0189", "\u0256"),
    ("\u018A", "\u0257"),
    ("\u018B", "\u018C"),
    ("\u018E", "\u01DD"),
    ("\u018F", "\u0259"),
    ("\u0190", "\u025B"),
    ("\u0191", "\u0192"),
    ("\u0193", "\u0260"),
    ("\u0194", "\u0263"),
    ("\u0196", "\u0269"),
    ("\u0197", "\u0268"),
    ("\u0198", "\u0199"),
    ("\u019C", "\u026F"),
    ("\u019D", "\u0272"),
    ("\u019F", "\u0275"),
    ("\u01A0", "\u01A1"),
    ("\u01A2", "\u01A3"),
    ("\u01A4", "\u01A5"),
    ("\u01A6", "\u0280"),
    ("\u01A7", "\u01A8"),
    ("\u01A9", "\u0283"),
    ("\u01AC", "\u01AD"),
    ("\u01AE", "\u0288"),
    ("\u01AF", "\u01B0"),
    ("\u01B1", "\u028A"),
    ("\u01B2", "\u028B"),
    ("\u01B3", "\u01B4"),
    ("\u01B5", "\u01B6"),
    ("\u01B7", "\u0292"),
    ("\u01B8", "\u01B9"),
    ("\u01BC", "\u01BD"),
    ("\u01C4", "\u01C6"),
    ("\u01C5", "\u01C6"),
    ("\u01C7", "\u01C9"),
    ("\u01C8", "\u01C9"),
    ("\u01CA", "\u01CC"),
    ("\u01CB", "\u01CC"),
    ("\u01CD", "\u01CE"),
    ("\u01CF", "\u01D0"),
    ("\u01D1", "\u01D2"),
    ("\u01D3", "\u01D4"),
    ("\u01D5", "\u01D6"),
    ("\u01D7", "\u01D8"),
    ("\u01D9", "\u01DA"),
    ("\u01DB", "\u01DC"),
    ("\u01DE", "\u01DF"),
    ("\u01E0", "\u01E1"),
    ("\u01E2", "\u01E3"),
    ("\u01E4", "\u01E5"),
    ("\u01E6", "\u01E7"),
    ("\u01E8", "\u01E9"),
    ("\u01EA", "\u01EB"),
    ("\u01EC", "\u01ED"),
    ("\u01EE", "\u01EF"),
    ("\u01F1", "\u01F3"),
    ("\u01F2", "\u01F3"),
    ("\u01F4", "\u01F5"),
    ("\u01F6", "\u0195"),
    ("\u01F7", "\u01BF"),
    ("\u01F8", "\u01F9"),
    ("\u01FA", "\u01FB"),
    ("\u01FC", "\u01FD"),
    ("\u01FE", "\u01FF"),
    ("\u0200", "\u0201"),
    ("\u0202", "\u0203"),
    ("\u0204", "\u0205"),
    ("\u0206", "\u0207"),
    ("\u0208", "\u0209"),
    ("\u020A", "\u020B"),
    ("\u020C", "\u020D"),
    ("\u020E", "\u020F"),
    ("\u0210", "\u0211"),
    ("\u0212", "\u0213"),
    ("\u0214", "\u0215"),
    ("\u0216", "\u0217"),
    ("\u0218", "\u0219"),
    ("\u021A", "\u021B"),
    ("\u021C", "\u021D"),
    ("\u021E", "\u021F"),
    ("\u0220", "\u019E"),
    ("\u0222", "\u0223"),
    ("\u0224", "\u0225"),
    ("\u0226", "\u0227"),
    ("\u0228", "\u0229"),
    ("\u022A", "\u022B"),
    ("\u022C", "\u022D"),
    ("\u022E", "\u022F"),
    ("\u0230", "\u0231"),
    ("\u0232", "\u0233"),
    ("\u023A", "\u2C65"),
    ("\u023B", "\u023C"),
    ("\u023D", "\u019A"),
    ("\u023E", "\u2C66"),
    ("\u0241", "\u0242"),
    ("\u0243", "\u0180"),
    ("\u0244", "\u0289"),
    ("\u0245", "\u028C"),
    ("\u0246", "\u0247"),
    ("\u0248", "\u0249"),
    ("\u024A", "\u024B"),
    ("\u024C", "\u024D"),
    ("\u024E", "\u024F"),
]


def build_to_lower():
    """Build the to_lower list."""
    max_upper = max(ord(t[0]) for t in _TO_LOWER)
    to_lower = [chr(i) for i in range(max_upper + 1)]
    for up, low in _TO_LOWER:
        offset = ord(up)
        to_lower[offset] = low
    return to_lower


TO_LOWER = build_to_lower()
