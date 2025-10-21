import kagglehub
import os
import pandas as pd
import sys
from core.lib import *

spellcheck_word = sys.argv[1]

# Set the path to the file you'd like to load
path = kagglehub.dataset_download("rtatman/english-word-frequency")
path_2 = kagglehub.dataset_download("bwandowando/479k-english-words")
file_path = os.path.join(path, "unigram_freq.csv")
file_path2 = os.path.join(path_2, "words_alpha.txt")
df_words_freq = pd.read_csv(file_path)
freq_map = dict(zip(df_words_freq['word'], df_words_freq['count']))
words_freq_set = set(df_words_freq['word'].values)
with open(file_path2, "r") as f:
    valid_words_set = set(line.strip() for line in f)

# Main program
if spellcheck_word in valid_words_set:
    print(f"The word '{spellcheck_word}' is spelled correctly.")
else:
    # Using Levenshtein distance to find suggestions
    time_start = pd.Timestamp.now()
    suggestion = levenshtein_distance_suggestion(spellcheck_word, valid_words_set, freq_map)
    time_end = pd.Timestamp.now()
    time_taken = time_end - time_start # Time taken: 0 days 00:00:00.086797
    print(suggestion)
    print(f"Time with Levenshtein distance: {time_taken.total_seconds():.3f}s {1/time_taken.total_seconds():.2f} words per second")
    
    # time_start = pd.Timestamp.now()
    # suggestion = levenshtein_distance_suggestion_chatgpt(spellcheck_word, valid_words_set, freq_map)
    # time_end = pd.Timestamp.now()
    # time_taken = time_end - time_start # Time taken: 0 days 00:00:00.086797
    # print(suggestion)
    # print(f"Time with Levenshtein distance by chatgpt: {time_taken.total_seconds():.3f}s {1/time_taken.total_seconds():.2f} words per second")
    # Using trigrams to find suggestions 
    time_start = pd.Timestamp.now()
    suggestion = trigram_suggestion(spellcheck_word, freq_map)
    time_end = pd.Timestamp.now()
    time_taken = time_end - time_start
    print(suggestion)
    print(f"Time with trigrams: {time_taken.total_seconds():.3f}s {1/time_taken.total_seconds():.2f} words per second")
    
    # # Using trigrams to find suggestions 
    # time_start = pd.Timestamp.now()
    # suggestion = trigram_suggestion_chatgpt(spellcheck_word, freq_map)
    # time_end = pd.Timestamp.now()
    # time_taken = time_end - time_start
    # print(suggestion)
    # print(f"Time with trigrams ChatGPT: {time_taken.total_seconds():.3f}s {1/time_taken.total_seconds():.2f} words per second")
