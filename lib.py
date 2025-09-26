# Spellcheker library functions

# Deletion complexity is O(n)
def deletion(spellcheck_word):
    """Create edits that delete one character."""
    edits = []
    for i in range(len(spellcheck_word)):
        edits.append(spellcheck_word[:i] + spellcheck_word[i+1:])
    return edits

# Insertion complexity is O(n*26)
def insertion(spellcheck_word):
    """Create edits that insert one character."""
    edits = []
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for i in range(len(spellcheck_word) + 1):
        for letter in alphabet:
            edits.append(spellcheck_word[:i] + letter + spellcheck_word[i:])
    return edits

# Replacement complexity is O(n*26)
def replacement(spellcheck_word):
    """Create edits that replace one character."""
    edits = []
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for i in range(len(spellcheck_word)):
        for letter in alphabet:
            edits.append(spellcheck_word[:i] + letter + spellcheck_word[i+1:])
    return edits

# Transposition is O(n)
def transposition(spellcheck_word):
    """Create edits that transpose two adjacent characters."""
    edits = []
    for i in range(len(spellcheck_word) - 1):
        edits.append(spellcheck_word[:i] + spellcheck_word[i+1] +
                     spellcheck_word[i] + spellcheck_word[i+2:])
    return edits

def lev_1_edits(spellcheck_word):
    """Create edits that are one edit away from the original word."""
    return (deletion(spellcheck_word) + insertion(spellcheck_word) +
            replacement(spellcheck_word) + transposition(spellcheck_word))

# The complexity is O(n^2 * 26^2) which is quite high
def lev_2_edits(spellcheck_word):
    """Create edits that are two edits away from the original word."""
    edits = set()
    for edit1 in (deletion(spellcheck_word) + insertion(spellcheck_word) +
                  replacement(spellcheck_word) + transposition(spellcheck_word)):
        for edit2 in (deletion(edit1) + insertion(edit1) +
                      replacement(edit1) + transposition(edit1)):
            edits.add(edit2)
    return edits

# The complexity of this approach is O(n*m) where n is the number of edits and m is the number of words in the dataframe
def lookup_suggestions(spellcheck_word, dict):
    """Lookup suggestions for a misspelled word."""
    suggestions = set()
    for edit in lev_1_edits(spellcheck_word):
        # this is slower because list lookups are O(n)
        if edit in dict['word'].values:
            suggestions.add(edit)
    # if suggestions is empty then do lev_2_edits
    if not suggestions:
        for edit in lev_2_edits(spellcheck_word):
            if edit in dict['word'].values:
                suggestions.add(edit)
    return suggestions

# The complexity of this approach is O(n) where n is the number of edits because hash lookups are O(1)
def lookup_suggestions_omptimized(spellcheck_word, dict):
    """Lookup suggestions for a misspelled word."""
    suggestions = set()
    # this is faster because set lookups are O(1)
    df_words_set = set(dict['word'].values)
    for edit in lev_1_edits(spellcheck_word):
        if edit in df_words_set:
            suggestions.add(edit)
    # if suggestions is empty then do lev_2_edits
    if not suggestions:
        edits_2 = lev_2_edits(spellcheck_word)
        for edit in edits_2:
            if edit in df_words_set:
                suggestions.add(edit)
    return suggestions
