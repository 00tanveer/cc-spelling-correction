import kagglehub
import os
import pandas as pd
import sys

print("spellcheck word", sys.argv[1])
spellcheck_word = sys.argv[1]

# Set the path to the file you'd like to load
path = kagglehub.dataset_download("rtatman/english-word-frequency")

# List files in the downloaded directory
files = os.listdir(path)

file_path = os.path.join(path, "unigram_freq.csv")
df = pd.read_csv(file_path)

time_start = pd.Timestamp.now()
if spellcheck_word in df['word'].values:
    print(f"The word '{spellcheck_word}' is spelled correctly.")
else:
    print(
        f"The word '{spellcheck_word}' is not found in the dataset. We suggest checking the spelling.")


def deletion(spellcheck_word):
    """Create edits that delete one character."""
    edits = []
    for i in range(len(spellcheck_word)):
        edits.append(spellcheck_word[:i] + spellcheck_word[i+1:])
    return edits


def insertion(spellcheck_word):
    """Create edits that insert one character."""
    edits = []
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for i in range(len(spellcheck_word) + 1):
        for letter in alphabet:
            edits.append(spellcheck_word[:i] + letter + spellcheck_word[i:])
    return edits


def replacement(spellcheck_word):
    """Create edits that replace one character."""
    edits = []
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    for i in range(len(spellcheck_word)):
        for letter in alphabet:
            edits.append(spellcheck_word[:i] + letter + spellcheck_word[i+1:])
    return edits


def transposition(spellcheck_word):
    """Create edits that transpose two adjacent characters."""
    edits = []
    for i in range(len(spellcheck_word) - 1):
        edits.append(spellcheck_word[:i] + spellcheck_word[i+1] +
                     spellcheck_word[i] + spellcheck_word[i+2:])
    return edits


"""Check if any edits are in the dataframe and print them."""
for edit in insertion(spellcheck_word):
    if edit in df['word'].values:
        print("insertion edits:", edit)
for edit in replacement(spellcheck_word):
    if edit in df['word'].values:
        print("replacement edits:", edit)
for edit in transposition(spellcheck_word):
    if edit in df['word'].values:
        print
for edit in deletion(spellcheck_word):
    if edit in df['word'].values:
        print("deletion edits:", edit)

time_end = pd.Timestamp.now()
print("time taken:", time_end - time_start)
