#include "line_align.hpp"
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

// This is a utility function for converting a string from UTF-32 to UTF-8
std::string convert_32_8(const std::u32string &wides) {
    std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> conv;
    return conv.to_bytes(wides);
}

// This is a utility function for converting a string from UTF-8 to UTF-32
std::u32string convert_8_32(const std::string &bytes) {
    std::wstring_convert<std::codecvt_utf8<char32_t>, char32_t> conv;
    return conv.from_bytes(bytes);
}

int64_t levenshtein(const std::u32string &str1, const std::u32string &str2) {
    const int64_t len1 = str1.length();
    const int64_t len2 = str2.length();

    if (len1 == 0) {
        return len2;
    }
    if (len2 == 0) {
        return len1;
    }

    std::vector<int64_t> dist(len2 + 1);
    std::iota(dist.begin(), dist.end(), 0);

    for (int64_t row = 0; row < len1; ++row) {
        int64_t prev_dist = row;
        for (int64_t col = 0; col < len2; ++col) {
            dist[col + 1] = std::min({std::exchange(prev_dist, dist[col + 1]) +
                                          (str1[row] == str2[col] ? 0 : 1),
                                      dist[col] + 1, dist[col + 1] + 1});
        }
    }
    return dist[len2];
}

std::vector<std::tuple<int64_t, int64_t, int64_t>>
levenshtein_all(const std::vector<std::u32string> &strings) {
    const int64_t len = strings.size();

    std::vector<std::tuple<int64_t, int64_t, int64_t>> results;

    for (int64_t row = 0; row < len - 1; ++row) {
        for (int64_t col = row + 1; col < len; ++col) {
            auto dist = levenshtein(strings[row], strings[col]);
            results.push_back(std::make_tuple(dist, row, col));
        }
    }

    std::stable_sort(results.begin(), results.end(),
                     [](auto const &tuple1, auto const &tuple2) {
                         return std::get<0>(tuple1) < std::get<0>(tuple2);
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
    Trace() : val(0.0), up(0.0), left(0.0), dir(none) {}
};
typedef std::vector<std::vector<Trace>> TraceMatrix;

std::vector<std::u32string>
align_all(const std::vector<std::u32string> &strings,
          const std::unordered_map<std::u32string, float> &substitutions,
          const float gap, const float skew) {
    if (strings.size() < 2) {
        return strings;
    }
    std::vector<std::u32string> results;
    results.push_back(strings[0]);

    for (size_t s = 1; s < strings.size(); ++s) {
        // Build the matrix
        size_t rows = results[0].length();
        size_t cols = strings[s].length();

        TraceMatrix trace(rows + 1, std::vector<Trace>(cols + 1));

        float penalty = gap;
        for (size_t row = 1; row <= rows; ++row) {
            trace[row][0].val = penalty;
            trace[row][0].up = penalty;
            trace[row][0].left = penalty;
            trace[row][0].dir = up;
            penalty += skew;
        }

        penalty = gap;
        for (size_t col = 1; col <= cols; ++col) {
            trace[0][col].val = penalty;
            trace[0][col].up = penalty;
            trace[0][col].left = penalty;
            trace[0][col].dir = left;
            penalty += skew;
        }

        for (size_t row = 1; row <= rows; ++row) {
            for (size_t col = 1; col <= cols; ++col) {
                Trace &cell = trace[row][col];
                Trace &cell_up = trace[row - 1][col];
                Trace &cell_left = trace[row][col - 1];

                cell.up = std::max({cell_up.up + skew, cell_up.val + gap});
                cell.left = std::max({cell_left.left + skew, cell_left.val + gap});

                float diagonal = std::numeric_limits<float>::lowest();
                for (size_t k = 0; k < results.size(); ++k) {
                    char32_t results_char = results[k][rows - row];
                    char32_t strings_char = strings[s][cols - col];

                    if (results_char == gap_char) {
                        continue;
                    }

                    if (results_char > strings_char) {
                        std::swap(strings_char, results_char);
                    }

                    std::u32string key = U"";
                    key += results_char;
                    key += strings_char;
                    float value;
                    try {
                        value = substitutions.at(key);
                    } catch (std::out_of_range &e) {
                        std::stringstream err;
                        err << "Either of '" << convert_32_8(key)
                            << "' these characters are missing from the "
                            << "substitution matrix.";
                        throw std::invalid_argument(err.str());
                    }
                    diagonal = value > diagonal ? value : diagonal;
                }
                diagonal += trace[row - 1][col - 1].val;
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
        int64_t row = rows;
        int64_t col = cols;
        std::u32string new_string;

        std::vector<std::u32string> new_results;
        for (size_t k = 0; k < results.size(); ++k) {
            new_results.push_back(U"");
        }

        while (true) {
            Trace cell = trace[row][col];
            if (cell.dir == none) {
                break;
            }

            if (cell.dir == diag) {
                for (size_t k = 0; k < results.size(); ++k) {
                    new_results[k] += results[k][rows - row];
                }
                new_string += strings[s][cols - col];
                --row;
                --col;
            } else if (cell.dir == up) {
                for (size_t k = 0; k < results.size(); ++k) {
                    new_results[k] += results[k][rows - row];
                }
                new_string += gap_char;
                --row;
            } else {
                for (size_t k = 0; k < results.size(); ++k) {
                    new_results[k] += gap_char;
                }
                new_string += strings[s][cols - col];
                --col;
            }
        }
        new_results.push_back(new_string);
        results = new_results;
    }

    return results;
}
