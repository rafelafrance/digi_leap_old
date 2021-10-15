#include <algorithm>
#include <codecvt>
#include <cstddef>
#include <exception>
#include <iostream>
#include <iterator>
#include <limits>
#include <locale>
#include <numeric>
#include <sstream>
#include <utility>
#include "string_align.hpp"

// This is a utility function for converting a string from UTF-32 to UTF-8
std::string convert_32_8(const std::u32string &bytes) {
    std::wstring_convert<std::codecvt_utf8<char32_t>,char32_t> conv;
    return conv.to_bytes(bytes);
}

// This is a utility function for converting a string from UTF-8 to UTF-32
std::u32string convert_8_32(const std::string &wide) {
    std::wstring_convert<std::codecvt_utf8<char32_t>,char32_t> conv;
    return conv.from_bytes(wide);
}

long levenshtein(const std::u32string& str1, const std::u32string& str2) {
    const long len1 = str1.length();
    const long len2 = str2.length();

    if (len1 == 0) { return len2; }
    if (len2 == 0) { return len1; }

    std::vector<long> dist(len2 + 1);
    std::iota(dist.begin(), dist.end(), 0);

    for (long r = 0; r < len1; ++r) {
        long prev_dist = r;
        for (long c = 0; c < len2; ++c) {
            dist[c + 1] = std::min({
                std::exchange(prev_dist, dist[c + 1]) + (str1[r] == str2[c] ? 0 : 1),
                dist[c] + 1,
                dist[c + 1] + 1
            });
        }
    }
    return dist[len2];
}

std::vector<std::tuple<long, long, long>>
levenshtein_all(const std::vector<std::u32string>& strings) {
    const long len = strings.size();

    std::vector<std::tuple<long, long, long>> results;

    for (long r = 0; r < len - 1; ++r) {
        for (long c = r + 1; c < len; ++c) {
            auto dist = levenshtein(strings[r], strings[c]);
            results.push_back(std::make_tuple(dist, r, c));
        }
    }

    std::stable_sort(results.begin(), results.end(),
        [](auto const &t1, auto const &t2) {
            return std::get<0>(t1) < std::get<0>(t2);
        });

    return results;
}

// Structures supporting the align_all() function.
enum TraceDir { none, diag, up, left };
struct Trace {
    float val;
    float up;
    float left;
    TraceDir dir;
    Trace(): val(0.0), up(0.0), left(0.0), dir(none) {}
};
typedef std::vector<std::vector<Trace>> TraceMatrix;

// TODO Make sure that pybind11 strings and weight matrix are not copied every time
std::vector<std::u32string>
align_all(
        const std::vector<std::u32string>& strings,
        const std::unordered_map<std::u32string, float>& weight,
        const float gap,
        const float skew
) {
    if (strings.size() < 1) {
        throw std::invalid_argument("You must enter at least one string.");
    }
    std::cout.precision(2);

    std::vector<std::u32string> results;

    results.push_back(strings[0]);

    for (size_t s = 1; s < strings.size(); ++s) {
        // Build the matrix
        size_t rows = results[0].length();
        size_t cols = strings[s].length();

        TraceMatrix trace(rows + 1, std::vector<Trace>(cols + 1));

        float g = gap;
        for (size_t r = 1; r <= rows; ++r) {
            trace[r][0].val = g;
            trace[r][0].up = g;
            trace[r][0].left = g;
            trace[r][0].dir = up;
            g += skew;
        }

        g = gap;
        for (size_t c = 1; c <= cols; ++c) {
            trace[0][c].val = g;
            trace[0][c].up = g;
            trace[0][c].left = g;
            trace[0][c].dir = left;
            g += skew;
        }

        for (size_t r = 1; r <= rows; ++r) {
            for (size_t c = 1; c <= cols; ++c) {
                Trace& cell = trace[r][c];
                Trace& cell_up = trace[r-1][c];
                Trace& cell_left = trace[r][c-1];

                cell.up = std::max({cell_up.up + skew, cell_up.val + gap});
                cell.left = std::max({cell_left.left + skew, cell_left.val + gap});

                float diagonal = std::numeric_limits<float>::lowest();
                for (size_t k = 0; k < results.size(); ++k) {
                    char32_t results_char = results[k][rows-r];
                    char32_t strings_char = strings[s][cols-c];

                    if (results_char == gap_char) { continue; }

                    if (results_char > strings_char) {
                        std::swap(strings_char, results_char);
                    }

                    std::u32string key = U"";
                    key += results_char;
                    key += strings_char;
                    float value;
                    try {
                        value = weight.at(key);
                    } catch (std::out_of_range& e) {
                        std::stringstream err;
                        err << "Either of '" << convert_32_8(key)
                            << "' these characters are missing from the "
                            << "substitution matrix.";
                        throw std::invalid_argument(err.str());
                    }
                    diagonal = value > diagonal ? value : diagonal;
                }
                diagonal += trace[r-1][c-1].val;
                cell.val = std::max({diagonal, cell.up, cell.left});

                if (cell.val == diagonal) {
                    cell.dir = diag;
                } else if (cell.val == cell.up) {
                    cell.dir = up;
                } else {
                    cell.dir = left;
                }
            }
        }

        // Trace-back
        long r = rows;
        long c = cols;
        std::u32string new_string;

        std::vector<std::u32string> new_results;
        for (size_t k = 0; k < results.size(); ++k) {
            new_results.push_back(U"");
        }

        while (true) {
            Trace cell = trace[r][c];
            if (cell.dir == none) {
                break;
            }

            if (cell.dir == diag) {
                for (size_t k = 0; k < results.size(); ++k) {
                    new_results[k] += results[k][rows-r];
                }
                new_string += strings[s][cols-c];
                --r;
                --c;
            } else if (cell.dir == up) {
                for (size_t k = 0; k < results.size(); ++k) {
                    new_results[k] += results[k][rows-r];
                }
                new_string += gap_char;
                --r;
            } else {
                for (size_t k = 0; k < results.size(); ++k) {
                    new_results[k] += gap_char;
                }
                new_string += strings[s][cols-c];
                --c;
            }
        }
        new_results.push_back(new_string);
        results = new_results;
    }

    return results;
}
