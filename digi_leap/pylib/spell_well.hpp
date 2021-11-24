#pragma once

#include <regex>
#include <string>
#include <unordered_map>
#include <vector>

/**
 * Modified from: Copyright (c) 2007-2016 Peter Norvig
 * See http://norvig.com/spell-correct.html
 * MIT license: www.opensource.org/licenses/mit-license.php
 */

const std::unordered_map<std::u32string, long> defaultVocab = {};
const std::u32string defaultReplacers = U"abcdefghijklmnopqrstuvwxyz";
const std::regex defaultDelimiter = std::regex(R"([[:lower:]]+)");

struct SpellWell {
    /**
     * Constructor.
     *
     * @param vocab A map of words to their frequencies.
     * @param replacers What characters to use for character replacement.
     * @param min_freq Exclude words from the vocab with a frequency lower than this.
     * @param min_len Exclude words from the vocab with a length lower than this.
     */
    SpellWell(
        const std::unordered_map<std::u32string, long>& vocab = defaultVocab,
        const std::u32string& replacers = defaultReplacers,
        long min_freq = 5,
        long min_len = 3);

    // std::u32string normalize(const std::u32string& word) const;

    /**
     * tokenize
     *
     * @param text The text to tokenize.
     * @return A list of tokens.
     */
    // std::vector<std::u32string> tokenize(
    //     const std::u32string& text,
    //     const std::regex& delimiter = defaultDelimiter) const;

private:
    std::unordered_map<std::u32string, long> vocab;
    std::u32string replacers;
    long min_freq;
    long min_len;
};
