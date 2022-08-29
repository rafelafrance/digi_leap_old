use std::cmp;
use std::collections::HashMap;

/// Compute the Levenshtein distance of 2 strings.
///
/// The Levenshtein distance is the count of the miminum number of edits that will
/// convert one string into another string. The allowed operations are
/// insertion/deletion and subsutitution. The distance is returned as an integer,
/// the lower the number the more similar the strings where 0 means they are identical.
///
/// Example: LineAlign::levenshtein("abcd", "a.cd"); will return 1
///
/// A modification of: https://en.wikipedia.org/wiki/Levenshtein_distance
///
pub fn levenshtein(s_line: &str, t_line: &str) -> u32 {
    let s_chars: Vec<char> = s_line.chars().collect();
    let t_chars: Vec<char> = t_line.chars().collect();
    let t_len = t_chars.len();

    let mut v0: Vec<u32> = (0..=t_len as u32).collect();
    let mut v1: Vec<u32> = (0..=t_len as u32).map(|_| 0).collect();

    for (i, s_char) in s_chars.iter().enumerate() {
        v1[0] = i as u32 + 1;

        for j in 0..t_len {
            let del = v0[j + 1] + 1;
            let ins = v1[j] + 1;
            let sub = if s_char == &t_chars[j] {
                v0[j]
            } else {
                v0[j] + 1
            };
            let min = cmp::min(del, cmp::min(ins, sub));
            v1[j + 1] = min;
        }
        (v0, v1) = (v1, v0);
    }

    v0[t_len]
}

/// Compute a Levenshtein distance for every pair of strings in list.
///    It returns A sorted list of tuples. The tuple contains:
///        1. The Levenshtein distance of the pair of strings.
///        2. The index of the first string compared.
///        3. The index of the second string compared.
///    The tuples are sorted by distance.
///
///    Example: LineAlign::levenshtein_all(vec!["abc", "abcde", "abcd"]);
///    will return vec![(1, 0, 2), (1, 1, 2), (2, 0, 1)]
///
pub fn levenshtein_all(lines: Vec<&str>) -> Vec<(u32, u32, u32)> {
    let mut results: Vec<(u32, u32, u32)> = Vec::new();
    for (i, ln1) in lines.iter().enumerate().take(lines.len() - 1) {
        for (j, ln2) in lines.iter().enumerate().skip(i + 1) {
            let result = levenshtein(ln1, ln2);
            results.push((result, i as u32, j as u32));
        }
    }
    results.sort();
    results
}

/// This contains parameters for aligning text sequences.
///     gap_char = is the character used when one sequence has a gap in the alignment.
///     substitutions = The substitution matrix given as a map, with the key as
///         a two character string representing the two character being substituted.
///         Symmetry is assumed so you only need to give the lexically first of a pair,
///         i.e. for "ab" and "ba" you only need to send in "ab". The value of the map
///         is the cost of substituting the two characters.
///     gap = The gap open penalty for alignments. This is typically negative.
///     skew = The gap extension penalty for the alignments. Also negative.
///
pub struct LineAlign {
    pub gap_char: char,
    pub gap: f32,
    pub skew: f32,
    pub substitutions: HashMap<(char, char), f32>,
}

enum TraceDir { None, Diag, Up, Left }
struct Trace {
    val: f32,
    up: f32,
    left: f32,
    dir: TraceDir,
}

type TraceMatrix = Vec<Vec<Trace>>;

/// Create a multiple sequence alignment of a set of similar short text fragments.
/// For example, given the parameters and the following set of strings:
///
/// my_line_align.align(vec![
///     "MOJAVE DESERT, PROVIDENCE MTS.: canyon above",
///     "E. MOJAVE DESERT , PROVIDENCE MTS . : canyon above",
///     "E MOJAVE DESERT PROVTDENCE MTS. # canyon above",
///     "Be ‘MOJAVE DESERT, PROVIDENCE canyon “above"
/// ]);
///
/// I should get back something similar to the following. The exact return value
/// will depend on the substitution matrix, gap, and skew penalties passed to the
/// function.
///
/// vec![
///     "⋄⋄⋄⋄MOJAVE DESERT⋄, PROVIDENCE MTS.⋄⋄: canyon ⋄above",
///     "E⋄. MOJAVE DESERT , PROVIDENCE MTS . : canyon ⋄above",
///     "E⋄⋄ MOJAVE DESERT ⋄⋄PROVTDENCE MTS. #⋄ canyon ⋄above",
///     "Be ‘MOJAVE DESERT⋄, PROVIDENCE ⋄⋄⋄⋄⋄⋄⋄⋄canyon “above"
/// ];
///
/// Where "⋄" characters are used to represent gaps in the alignments.
///
impl LineAlign {
    pub fn new(substitutions: HashMap<(char, char), f32>, gap: f32, skew: f32) -> Self {
        Self {
            gap_char: '⋄',
            gap,
            skew,
            substitutions,
        }
    }

    pub fn align(&self, lines: Vec<&str>) -> Vec<String> {
        if lines.len() <= 1 {
            let results = lines.iter().map(|ln| ln.to_string()).collect();
            return results;
        }
        let mut results: Vec<String> = vec![ lines[0].to_string() ];

        for (s, ln) in lines.iter().enumerate().skip(1) {
            let rows = results[0].len();
            let cols = ln.len();
            let mut trace: TraceMatrix = Vec::new();

            let mut penalty = self.gap;
            for row in 1..=rows {
                trace[row][0].val = penalty;
                trace[row][0].up = penalty;
                trace[row][0].left = penalty;
                trace[row][0].dir = TraceDir::Up;
                penalty += self.skew;
            }

            penalty = self.gap;
            for col in 1..=cols {
                trace[0][col].val = penalty;
                trace[0][col].up = penalty;
                trace[0][col].left = penalty;
                trace[0][col].dir = TraceDir::Left;
                penalty += self.skew;
            }

            for row in 1..=rows {
                for col in 1..=cols {
                    let mut cell = &trace[row][col];
                    let cell_up = &trace[row-1][col];
                    let cell_left = &trace[row][col -1];

                    cell.up = cmp::max(cell_up.up + self.skew, cell_up.val + self.gap);
                    cell.left = cmp::max(cell_left.left + self.skew, cell_left.val + self.gap);
                }
            }
        }

        results
    }
}


// ====================================================================================
#[cfg(test)]
mod tests {
    use crate::{levenshtein, levenshtein_all};
    #[test]
    fn levenshtein_it_works() {
        let actual = levenshtein("abcde", "abcde");
        assert_eq!(actual, 0);
    }
    #[test]
    fn levenshtein_one_before() {
        let actual = levenshtein("_abc", ".abc");
        assert_eq!(actual, 1);
    }
    #[test]
    fn levenshtein_two_before_ragged() {
        let actual = levenshtein("..abc", "abc");
        assert_eq!(actual, 2);
    }
    #[test]
    fn levenshtein_two_after() {
        let actual = levenshtein("abc..", "abc__");
        assert_eq!(actual, 2);
    }
    #[test]
    fn levenshtein_two_middle_not_contiguous() {
        let actual = levenshtein("a.b.c", "a_b_c");
        assert_eq!(actual, 2);
    }
    #[test]
    fn levenshtein_three_middle_contiguous() {
        let actual = levenshtein("a...c", "a___c");
        assert_eq!(actual, 3);
    }
    #[test]
    fn levenshtein_one_wide_char() {
        let actual = levenshtein("五五", "五六");
        assert_eq!(actual, 1);
    }
    #[test]
    fn levenshtein_missing_1st() {
        let actual = levenshtein("", "五六");
        assert_eq!(actual, 2);
    }
    #[test]
    fn levenshtein_missing_2nd() {
        let actual = levenshtein("五五", "");
        assert_eq!(actual, 2);
    }
    #[test]
    fn levenshtein_all_it_works() {
        let lines = vec![
            "MOJAVE DESERT, PROVIDENCE MTS.: canyon above",
            "E. MOJAVE DESERT , PROVIDENCE MTS . : canyon above",
            "E MOJAVE DESERT PROVTDENCE MTS. # canyon above",
            "Be ‘MOJAVE DESERT, PROVIDENCE canyon “above",
        ];
        let expect = vec![
            (6, 0, 1),
            (6, 0, 2),
            (6, 1, 2),
            (11, 0, 3),
            (13, 1, 3),
            (13, 2, 3),
        ];
        let actual = levenshtein_all(lines);
        assert_eq!(expect, actual);
    }
    #[test]
    fn levenshtein_all_example() {
        let actual = levenshtein_all(vec!["abc", "abcde", "abcd"]);
        let expect = vec![(1, 0, 2), (1, 1, 2), (2, 0, 1)];
        assert_eq!(expect, actual);
    }
}
