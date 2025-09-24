# Instroduction
This is a coding challenge (number 98) by John Crickett. The prompt is to create my own spelling correction tool, learn about different approaches and try to do my best to document my learnings. I'm using a word frequency database ([the English word frequency dataset](https://www.kaggle.com/datasets/rtatman/english-word-frequency?resource=download) from Kaggle) match the word inputs.

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

## Performance
Once the transofmations are done, we can do the lookup of the words in the word frequency table in 2 ways.