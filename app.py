import kagglehub
import os
import pandas as pd
import sys
from lib import *
spellcheck_word = sys.argv[1]

# Set the path to the file you'd like to load
path = kagglehub.dataset_download("rtatman/english-word-frequency")
path_2 = kagglehub.dataset_download("bwandowando/479k-english-words")

# List files in the downloaded directory
files = os.listdir(path)
files_2 = os.listdir(path_2)

file_path = os.path.join(path, "unigram_freq.csv")
file_path_2 = os.path.join(path_2, "words_alpha.txt")
df_words_freq = pd.read_csv(file_path)
df_correct_words = pd.read_csv(file_path_2, names=['word'])


# Main program
time_start = pd.Timestamp.now()
if spellcheck_word in df_correct_words['word'].values:
    print(f"The word '{spellcheck_word}' is spelled correctly.")
else:
    print(
        f"The word '{spellcheck_word}' is most likely misspelled.")
    suggestions = lookup_suggestions_optimized(
        spellcheck_word, df_words_freq)

    print("The suggestions are: ", suggestions)
    time_end = pd.Timestamp.now()
    print("Time taken:", time_end - time_start)
    # calculate frequency of words[] in df and sort by frequency
    words_df = df_words_freq[df_words_freq['word'].isin(suggestions)].sort_values(
        by='count', ascending=False)
    print("Did you mean this word?")
    # print the topmost suggestion
    if not words_df.empty:
        print(words_df.iloc[0]['word'])


