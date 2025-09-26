import kagglehub
import os
import pandas as pd
import sys
from lib import *

spellcheck_word = sys.argv[1]

# Set the path to the file you'd like to load
path = kagglehub.dataset_download("rtatman/english-word-frequency")
path_2 = kagglehub.dataset_download("bwandowando/479k-english-words")
file_path = os.path.join(path, "unigram_freq.csv")
file_path2 = os.path.join(path_2, "words_alpha.txt")
df_words_freq = pd.read_csv(file_path)
df_word_dict = pd.read_csv(file_path2, names=['word'])

# Main program
time_start = pd.Timestamp.now()
if spellcheck_word in df_word_dict['word'].values:
    print(f"The word '{spellcheck_word}' is spelled correctly.")
else:
    suggestions = lookup_suggestions_optimized(spellcheck_word, df_word_dict)
    # print(f"The word '{spellcheck_word}' is most likely misspelled.")
    # calculate frequency of words[] in df and sort by frequency
    words_df = df_words_freq[df_words_freq['word'].isin(suggestions)].sort_values(
        by='count', ascending=False)
    # print("Did you mean this word?")
    # print the topmost suggestion
    if not words_df.empty:
        print(words_df.iloc[0]['word'])
        #time_taken in seconds
        time_end = pd.Timestamp.now()
        time_taken = time_end - time_start # Time taken: 0 days 00:00:00.086797
        print(f"Time: {time_taken.total_seconds():.3f}s {1/time_taken.total_seconds():.2f} words per second")
