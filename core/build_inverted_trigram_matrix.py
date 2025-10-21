import kagglehub 
import os 
import pandas as pd
import sys 
import json

path = kagglehub.dataset_download("bwandowando/479k-english-words")
file_path = os.path.join(path, "words_alpha.txt")
df_words = pd.read_csv(file_path, header=None, names=["word"])

# Drop the nan values
df_words = df_words.dropna()

# The complexity of this approach is O(n*m) where n is the number of trigrams and m is the number of words in the dataframe
# Create an inverted index of trigrams to words
df_words['trigrams'] = df_words['word'].apply(lambda x: [x[i:i+3] for i in range(len(x)-2)] if len(x) >= 3 else [])
inverted_trigram_index = {}
for index, row in df_words.iterrows():
    word = row['word']
    trigrams = row['trigrams']
    for trigram in trigrams:
        if trigram not in inverted_trigram_index:
            inverted_trigram_index[trigram] = set()
            inverted_trigram_index[trigram].add(word)
        else:
            inverted_trigram_index[trigram].add(word)
print(list(inverted_trigram_index.items())[:5])
# Convert all sets to lists because sets are not JSON serializable
inverted_trigram_index_serializable = {k: list(v) for k, v in inverted_trigram_index.items()}
# Save the inverted index to a JSON file because  JSON handles Python lists and dictionaries natively
with open('inverted_trigram_index.json', 'w') as f:
    json.dump(inverted_trigram_index_serializable, f)