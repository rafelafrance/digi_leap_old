#pragma once

#include <string>
#include <unordered_map>

/**
 * Modified from: Copyright (c) 2007-2016 Peter Norvig
 * See http://norvig.com/spell-correct.html
 * MIT license: www.opensource.org/licenses/mit-license.php
 */

struct SpellWell {
    /**
     * Constructor.
     *
     * @param vocab A map of words to their frequencies.
     * @param lowers What characters to use for character replacement.
     * @param min_freq Exclude words from the vocab with a frequency lower than this.
     * @param min_len Exclude words from the vocab with a length lower than this.
     */
    SpellWell(
        const std::unordered_map<std::u32string, long>& vocab,
        const std::u32string& lowers,
        const long min_freq = 5,
        const long min_len = 3
        ) : vocab(vocab), lowers(lowers), min_freq(min_freq), min_len(min_len) {};

private:
    const std::unordered_map<std::u32string, long>& vocab;
    const std::u32string& lowers;
    const long min_freq;
    const long min_len;
};
