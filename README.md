# Introduction
This is a coding challenge (number 98) by John Crickett. The prompt is to create my own spelling correction tool, learn about different approaches and try to do my best to document my learnings. I'm using a word frequency dataset ([the English word frequency dataset](https://www.kaggle.com/datasets/rtatman/english-word-frequency?resource=download) from Kaggle) and an English word list dataset ([Dataset containing 479k words](https://www.kaggle.com/datasets/bwandowando/479k-english-words?select=words_alpha.txt)). 

Do note that the word frequency dataset also contains highly frequent misspelled words. So, we will need to first use the authoritaive English word dataset to first assess whether any input is an incorrect spelling. Then, I use the word frequency dataset to figure out what the top suggestions should be. It's a reliable heuristic that from words that have the same Levenshtein distances or the same trigram coverage, the likeliest correctly spelled word suggestion is the one that occurs the most in any text corpus.

# Program structure
This is a command line program written in Python. The main program is contained in the `app.py` file. Instructions to run this program:
`python app.py [word]` The program doesn't take multiple inputs/arugements yet.

The desired output:
1. List of the best word suggestion that is achieved by either Levenshtein distance edits or trigrams. 
2. The time it took to find the top-most suggestion.

# Algorithms tested
## One letter transformations - Levenshtein distance=1
The assumption is that in the incorrect word, just one character is missing, incorrect or swapped with the adjacent character by mistake. These incorrect words have a Levenshtein distance of 1.

Insertion, replacement, transposition and deletion are the transormations we can make on the incorrect word to get the correctly spelled word
Insertion can deal with characters missing. `hring -> hiring`
Replacement and deletion can deal with incorrect characters. `barryster -> barrister barristerr -> barrister`
Transposition deals with letters swapped. `barritser -> barrister`

## Two letter transformations - Levenshtein distance (ld)=2
We can do this by:
1. coming up with all ld=1 edits of the incorrect spelling first. 
2. Then, doing another round of transformation on all the edits from the previous procedure.

## Trigrams
The approach is to pre-build a trigram index of all English dictionary words. [speed -> 'spe', 'pee', 'eed'; enamor -> 'ena', 'nam', 'amo', 'mor'; and so on for all other words in the dictionary]. We build this trigram index and invert it, that is, create a map of trigram -> words. We persist this inverted index to be referencd later for spelling checking/correction.

For the misspelled word, we find all its trigrams that we reference with the inverted trigram index. From the trigram -> words map, we only keep words that are at most 2 letters more than the misspelled word. For every word in the trigram -> words list, we calculate how many trigrams they share with the misspelled word. Then we sort the coverage scores by word frequency (just like in Levenshtein edits), length of word and alphabetic order.

Considerations I didn't make:
- Unicode
- Alphanumeric cases

## Performance
Once the transofmations are done, we can do the lookup of the words in the word frequency table in 2 ways.
1. List lookup. O(n*m), n is the length of the input word, m is the size of the dictionary
2. Hash lookup, O(n*1)
3. In finding Levenshtein edits, Python generators give a performance boost for routines where we are trying to build a whole set of edits to iterate through. They are memory-efficient and lend faster execution times because data structures are processed and served on demand rather than all at once. Really helpful with large datasets. Will definitely keep generators in mind when 'yielding' values from large sequences in subsequent projects.
4. There are code stubs I borrowed from ChatGPT and kept them here for comparison purposes. I coded counterparts of the GPT generated versions to try to match their performance. Helped me to learn and internalized a lot better than using autocomplete.

The performance is tested with latency (time to generate one word) and throughput (total words processed per second) figures.
Time : 0.278s 11.9 words per second

### Algorithm complexities
1. Levenshtein distance=1 lookups are much faster. O(n), n=number of one-character edits required
2. Levenshtein distance=2 lookups are much slower. O(n^2 * a^2), n=number of one-character edits required and a=number of alphabets
3. Using trigrams, the complexity of the function I wrote can be broken down these major cost functions:
    - Building trigrams for the spelled word -> O(m), m=len(spellcheck_word)
    - Looking up candidate word sets from inverted trigram index. O(t), t=number of unique trigrams in the misspelled word
    - U is the union set of all correct words that share the trigrams from the misspelled word
    - For each candidate word in U, we iterate over all trigrams (t) to see how trigrams are common between the two. Worst case complexity is O(U*t)
    - Finally, we sort the candidates according to their frequency in the word frequencies dataset. That's O(UlogU) for the sorting function in Python.
    - So, the overall complexity is O(m+t+U*t+UlogU).
    - Approximated, that's O(U(1+logU)), U=uniot set of all correct English words
    - We could conclude that the complexity using trigrams to find the correct spelling depends on the size of the text corpus.

# Next steps for me
- Build a distribution of the nature of spelling mistakes.
- Combine Levenshtein and trigrams
- Benchmark against difference performance measures
- Launch a Python module
