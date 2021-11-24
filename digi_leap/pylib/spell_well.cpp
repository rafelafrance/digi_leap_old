#include "spell_well.hpp"
#include <locale>
#include <iostream>

SpellWell::SpellWell(
        const std::unordered_map<std::u32string, long>& vocab,
        const std::u32string& replacers, long min_freq, long min_len)
{
    this->vocab = vocab;
    this->replacers = replacers;
    this->min_freq = min_freq;
    this->min_len = min_len;
}

// std::u32string SpellWell::normalize(const std::u32string& word) const
// {
//     std::u32string result = word;
//     for (char32_t& c : result)
//     {
//     }
//     return result;
// }
