# Instroduction
This is a coding challenge (number 98) by John Crickett. The prompt is to create my own spelling correction tool, learn about different approaches and try to do my best to document my learnings. I'm using a word frequency dataset ([the English word frequency dataset](https://www.kaggle.com/datasets/rtatman/english-word-frequency?resource=download) from Kaggle) and an English word list dataset ([Dataset containing 479k words](https://www.kaggle.com/datasets/bwandowando/479k-english-words?select=words_alpha.txt)). 

Do note that the word frequency dataset also contains highly frequent misspelled words. So, we will need to first use the authoritaive English word dataset to first assess whether any input is an incorrect spelling. Then, I use the word frequency dataset to figure out what the top suggestions should be.

# Program structure
This is a command line program written in Python. The main program is contained in the `app.py` file. Instructions to run this program:
`python app.py [word]`
The desired output:
1. List of all word suggestions that are achieved by editing just one character of the incorrect input.
2. The time it took to find all the suggestions.
3. The topmost suggestion.

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

## Performance
Once the transofmations are done, we can do the lookup of the words in the word frequency table in 2 ways.
1. List lookup. O(n*m), n is the length of the input word, m is the size of the dictionary
2. Hash lookup, O(n*1)

The performance is tested by
Time : 0.278s 11.9 words per second, 
The time it takes to suggest the correct spelling and the number of words the program can correct per second.