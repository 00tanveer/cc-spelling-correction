import kagglehub
import os
import pandas as pd
import sys

spellcheck_word = sys.argv[1]

# Set the path to the file you'd like to load
path = kagglehub.dataset_download("rtatman/english-word-frequency")

# List files in the downloaded directory
files = os.listdir(path)

file_path = os.path.join(path, "unigram_freq.csv")
df = pd.read_csv(file_path)

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

# The complexity of this approach is O(n*m) where n is the number of edits and m is the number of words in the dataframe
def lookup_suggetions(spellcheck_word):
    """Lookup suggestions for a misspelled word."""
    suggestions = set()
    for edit in (deletion(spellcheck_word) + insertion(spellcheck_word) +
                 replacement(spellcheck_word) + transposition(spellcheck_word)):
        # this is slower because list lookups are O(n)
        if edit in df['word'].values:
            suggestions.add(edit)
    return suggestions

# The complexity of this approach is O(n) where n is the number of edits because hash lookups are O(1)
def lookup_suggetions_optimized(spellcheck_word):
    """Lookup suggestions for a misspelled word."""
    suggestions = set()
    edits = (deletion(spellcheck_word) + insertion(spellcheck_word) +
             replacement(spellcheck_word) + transposition(spellcheck_word))
    # this is faster because set lookups are O(1)
    df_words_set = set(df['word'].values)
    for edit in edits:
        if edit in df_words_set:
            suggestions.add(edit)
    return suggestions

# Main program
time_start = pd.Timestamp.now()
if spellcheck_word in df['word'].values:
    print(f"The word '{spellcheck_word}' is spelled correctly.")
else:
    print(
        f"The word '{spellcheck_word}' is most likely misspelled.")
    print("The suggestions are: ", lookup_suggetions_optimized(spellcheck_word))
    time_end = pd.Timestamp.now()
    print("Time taken:", time_end - time_start)

# calculate frequency of words[] in df and sort by frequency
words_df = df[df['word'].isin(lookup_suggetions_optimized(spellcheck_word))].sort_values(
    by='count', ascending=False)
print("Did you mean this word?")
# print the topmost suggestion
if not words_df.empty:
    print(words_df.iloc[0]['word'])