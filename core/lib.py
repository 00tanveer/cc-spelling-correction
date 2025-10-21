import json
import kagglehub
import os
import pandas as pd
from collections import Counter
from typing import Iterable, Iterator, Optional
from core.trie import Trie

path = kagglehub.dataset_download("rtatman/english-word-frequency")
file_path = os.path.join(path, "unigram_freq.csv")
df_words_freq = pd.read_csv(file_path)

path_2 = kagglehub.dataset_download("bwandowando/479k-english-words")
file_path2 = os.path.join(path_2, 'words_alpha.txt')
with open(file_path2, 'r') as f:
    valid_words = set(line.strip() for line in f)

with open('core/inverted_trigram_index.json', 'r') as f:
    inverted_trigram_index = json.load(f)

# Spellcheker library functions

# Deletion complexity is O(n)
def deletion(s):
    """Create edits that delete one character."""
    edits = []
    for i in range(len(s)):
        edits.append(s[:i] + s[i+1:])
    return edits

# Insertion complexity is O(n*26)
def insertion(s):
    """Create edits that insert one character."""
    edits = []
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for i in range(len(s) + 1):
        for letter in alphabet:
            edits.append(s[:i] + letter + s[i:])
    return edits

# Replacement complexity is O(n*26)
def replacement(s):
    """Create edits that replace one character."""
    edits = []
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for i in range(len(s)):
        for letter in alphabet:
            if letter != s[i]:
                edits.append(s[:i] + letter + s[i+1:])
    return edits

# Transposition is O(n)
def transposition(s):
    """Create edits that transpose two adjacent characters."""
    edits = []
    for i in range(len(s) - 1):
        edits.append(s[:i] + s[i+1] +
                     s[i] + s[i+2:])
    return edits

# not using a generator
def lev_1_edits(spellcheck_word):
    """Create edits that are one edit away from the original word."""
    return (deletion(spellcheck_word) + insertion(spellcheck_word) +
            replacement(spellcheck_word) + transposition(spellcheck_word))

def lev_1_edits_streamed(word):
    """Yield edits that are one edit away (lazy generator)."""
    n = len(word)
    ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
    # Deletions
    for i in range(n):
        yield word[:i] + word[i+1:]

    # Transpositions
    for i in range(n - 1):
        yield word[:i] + word[i+1] + word[i] + word[i+2:]

    # Replacements
    for i in range(n):
        for c in ALPHABET:
            if c != word[i]:  # skip same-letter replacement
                yield word[:i] + c + word[i+1:]

    # Insertions
    for i in range(n + 1):
        for c in ALPHABET:
            yield word[:i] + c + word[i:]
# The complexity is O(n^2 * 26^2) which is quite high
# def known_edits(word, words_set):
#     """
#         Stream only dictionary words at edit=2. We don't 
#         build the whole edit-2 set immediately. We generate-and-check 
#         immediately.
#     """
#     edits = set()
#     for e1 in lev_1_edits_streamed(word):


# The complexity of Levenshtein distance=1 is O(n) where n is the number of edits because hash lookups are O(1)
def levenshtein_distance_suggestion(spellcheck_word, words_set, freq_map):
    suggestions = set()
    # this is faster because set lookups are O(1)
    # df_words_set = set(dict['word'].values)
    edits_1 = {e for e in lev_1_edits_streamed(spellcheck_word) if e in words_set}
    valid_suggestions = [s for s in edits_1 if s in freq_map]
    if valid_suggestions:
        return max(valid_suggestions, key=freq_map.get)
    # if suggestions is empty then do lev_2_edits
    if not valid_suggestions:
        # get the d=1 edits, don't materialize the full d=2 edit set, 
        # lev transform the d=1 edit one by one, and check if it's in vocab and add to suggestions
        best_score = -1
        for word in lev_1_edits_streamed(spellcheck_word):
            for edit_2 in lev_1_edits_streamed(word):
                if edit_2 in words_set:
                    score = freq_map.get(edit_2, 0)
                    if score > best_score:
                        best_score = score
                        suggestions.add(edit_2)
                        if len(suggestions) == 3:
                            break
    print(suggestions)
    valid_suggestions = [s for s in suggestions if s in freq_map]
    if not suggestions:
        print("No Levenshtein distance=2 words from the input word is in the dictionary. You probably wrote gibberish.")
        return None
    return max(valid_suggestions, key=freq_map.get)


# using trigrams to find suggestions
# incorporates a trigram coverage filter, length of word filter, a word frequency filter
def trigram_suggestion(spellcheck_word, freq_map, inverted_trigram_index=inverted_trigram_index):
    spellcheck_word = spellcheck_word.casefold()
    if len(spellcheck_word) <3:
        return None
    misspelled_trigrams = [spellcheck_word[i:i+3] for i in range(len(spellcheck_word)-2)] 
    # print(misspelled_trigrams)

    curtailed_trigram_index = {}
     # Build curtailed index safely (no KeyError)
    curtailed_trigram_index = {
        tg: set(inverted_trigram_index.get(tg, ()))   # <- safe lookup
        for tg in misspelled_trigrams
    }
    # print(curtailed_trigram_index)
    # set of all correct words
    correct_words_sharing_trigrams = set()
    for list_of_words in curtailed_trigram_index.values():
        for word in list_of_words:
            correct_words_sharing_trigrams.add(word)
    correct_words_sharing_trigrams = {
        w for w in correct_words_sharing_trigrams if len(w) < len(spellcheck_word)+2
    }
    # count number of shared trigrams for each word that has trigram from misspelled word
    word_count = {}
    for word in correct_words_sharing_trigrams:
        word_count[word] = 0
        for values in curtailed_trigram_index.values():
            if word in values:
                word_count[word] = word_count[word] + 1
    # print(word_count)
    for key, value in word_count.items():
        # fraction of misspelled word's trigrams shared by candidate word
        word_count[key] = value/len(misspelled_trigrams)
    word_coverage = word_count
    # sort by similarity, word frequencies, length of word, then alphabetically (4 sorting parameters all in one sorting function)
    top_3 = sorted(
        word_coverage.items(), 
        key = lambda x: (-x[1], -freq_map.get(x[0], 0), len(x[0]), x[0]))[:3]
    # print(top_10)
    if top_3:
        top_most_suggestion = top_3[0][0]
        return top_most_suggestion

############## Spell check using tries ###############
import time
trie = Trie()
# insert all dictionary words
for word in valid_words:
    trie.insert(word)
# start = time.time()
# print(trie.search('beautifull'))
# end = time.time()
# print(f'Time taken by trie: {(end-start):.8f}s')
# start = time.time()
# print(word in valid_words)
# end = time.time()
# print(f'Time taken by in operator: {(end-start):.8f}s')

def search_trie_with_levenshtein(trie, word, max_edit=2):
    """
    Find all words in the trie within a given edit distance of 'word'.
    """

    results = []

    # Recursive DFS
    def dfs(node, prefix, previous_row):
        """
        node: current TrieNode
        prefix: prefix formed so far
        previous_row: list representing previous row of Levenshtein DP matrix
        """
        columns = len(word) + 1
        current_row = [previous_row[0] + 1]

        # Build current row of DP matrix (Levenshtein distance row)
        for column in range(1, columns):
            insert_cost = current_row[column - 1] + 1
            delete_cost = previous_row[column] + 1
            replace_cost = previous_row[column - 1] + (0 if word[column - 1] == prefix[-1] else 1)
            current_row.append(min(insert_cost, delete_cost, replace_cost))

        # If last cell <= max_edit and node is a word, collect it
        if current_row[-1] <= max_edit and node.is_end:
            results.append((prefix, current_row[-1]))

        # If any value in current_row ≤ max_edit, we can still explore deeper
        if min(current_row) <= max_edit:
            for char, child in node.children.items():
                dfs(child, prefix + char, current_row)

    # Initialize DP row for empty prefix
    initial_row = list(range(len(word) + 1))

    # Start DFS for each child of root
    for char, node in trie.root.children.items():
        dfs(node, char, initial_row)
    print("Results AREEEEE: ", results)
    return sorted(results, key=lambda x: (x[1], x[0]))
start = time.time()
query = "bevebolent"
results = search_trie_with_levenshtein(trie, query, max_edit=2)   
end = time.time()
print(f'Time taken by in operator: {(end-start):.8f}s {(1/(end-start)):.2f} words per second')
print(f"Suggestions for '{query}':")
print(results)
for word, dist in results:
    print(f"  {word} (distance={dist})")

#########################
def trigram_suggestion_chatgpt(spellcheck_word, freq_map, inverted_trigram_index=inverted_trigram_index):
    # normalize
    q = spellcheck_word.casefold()

    # short-word fallback
    if len(q) < 3:
        return None  # or spellcheck_word

    # unique trigrams for the query
    miss_trigs = {q[i:i+3] for i in range(len(q) - 2)}
    if not miss_trigs:
        return None

    # postings lookup (safe)
    hit_lists = [inverted_trigram_index.get(tg, ()) for tg in miss_trigs]

    # collect candidates via union
    candidates = set().union(*hit_lists)
    if not candidates:
        return None

    # symmetric length window (±2)
    candidates = {w for w in candidates if abs(len(w) - len(q)) <= 2}
    if not candidates:
        return None

    # count overlaps (unique-trigram overlap per candidate)
    counts = Counter()
    for tg in miss_trigs:
        counts.update(inverted_trigram_index.get(tg, ()))

    # compute coverage scores (over unique query trigrams)
    denom = len(miss_trigs)
    word_coverage = {w: counts[w] / denom for w in candidates if counts[w] > 0}
    if not word_coverage:
        return None

    # rank: coverage desc, freq desc, shorter first, alpha
    ranked = sorted(
        word_coverage.items(),
        key=lambda x: (-x[1], -freq_map.get(x[0], 0), len(x[0]), x[0])
    )[:3]

    # return best single suggestion (keep your API)
    return ranked[0][0] if ranked else None

ALPHABET = 'abcdefghijklmnopqrstuvwxyz'


def lev_1_edits(word: str) -> Iterator[str]:
    """
    Yield edits that are one edit away (delete, transpose, replace, insert).
    Implemented as a generator to avoid materializing huge lists.
    """
    n = len(word)

    # Deletions
    for i in range(n):
        yield word[:i] + word[i+1:]

    # Transpositions (adjacent swap)
    for i in range(n - 1):
        yield word[:i] + word[i+1] + word[i] + word[i+2:]

    # Replacements (skip replacing with the same character to reduce dups)
    for i in range(n):
        orig = word[i]
        for c in ALPHABET:
            if c != orig:
                yield word[:i] + c + word[i+1:]

    # Insertions
    for i in range(n + 1):
        for c in ALPHABET:
            yield word[:i] + c + word[i:]


def known_edits2(word: str, words_set: set[str]) -> Iterator[str]:
    """
    Stream *only* dictionary words at edit distance 2.
    We do NOT build the full edits-2 set; we generate-and-check immediately.
    """
    seen: set[str] = set()  # avoid yielding duplicates
    for e1 in lev_1_edits(word):
        for e2 in lev_1_edits(e1):
            if e2 in words_set and e2 not in seen:
                seen.add(e2)
                yield e2


def best_by_freq(candidates: Iterable[str], freq_map: dict[str, int]) -> Optional[str]:
    """
    Pick the candidate with the highest frequency (missing -> 0).
    Returns None if no candidates.
    """
    best = None
    best_score = -1
    for w in candidates:
        score = freq_map.get(w, 0)
        if score > best_score:
            best, best_score = w, score
    return best


def levenshtein_distance_suggestion_chatgpt(
    spellcheck_word: str,
    words_set: set[str],
    freq_map: dict[str, int],
    *,
    max_edits: int = 2,
    lowercase: bool = True,
    early_stop_ed2_hits: Optional[int] = None,
) -> Optional[str]:
    """
    Return the most frequent dictionary word within edit distance <= max_edits.
    - Streams edits1/edits2 (no huge intermediate sets).
    - Uses freq_map (dict) to rank.
    - If early_stop_ed2_hits is set (e.g., 3), we return as soon as that many
      distinct edit-2 dictionary hits are found (choosing the best among them).
    """

    w = spellcheck_word.lower() if lowercase else spellcheck_word

    # Edit distance 1: stream & filter immediately into a tiny set
    ed1_hits = {e for e in lev_1_edits(w) if e in words_set}
    if ed1_hits:
        return best_by_freq(ed1_hits, freq_map)

    if max_edits < 2:
        return None

    # Edit distance 2: stream and short-circuit optionally
    if early_stop_ed2_hits is None or early_stop_ed2_hits <= 0:
        # Simple streaming: no cap
        return best_by_freq(known_edits2(w, words_set), freq_map)

    # Early-stop version: keep only a few hits then decide
    hits: list[str] = []
    for cand in known_edits2(w, words_set):
        hits.append(cand)
        if len(hits) >= early_stop_ed2_hits:
            break

    return best_by_freq(hits, freq_map) if hits else None
