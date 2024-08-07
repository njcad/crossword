# crossword
Python crossword generation algorithm from arbitrary list of words

# input
Call `generate(wordlist: List[str], verbose: Bool)` with an arbitrary list of words from which to generate a crossword. If a crossword puzzle can be generated from this list of words, a relatively dense one will be generated. Note that not any list of words will work; if the list is too small and/or the words are too short, the generator may be unable to find a solution, even if one technically exists. The tradeoff here is that the algorithm is relatively fast at less than a second for long (around 30) lists of words. 

# output
The function `generate(wordlist: List[str], verbose: Bool)` will return a square grid structure for a completed crossword (solution) and a placement dictionary `{word number : [word, starting pos (row, col), direction 'H' or 'V']}` for reference to where each word occurs on the grid. 

# to do
Working on a UI for crossword logic output. Also working on a super-dense generation mode which will find super-dense solutions (like NYT crosswords) given a set of words which can technically make a crossword. Tradeoff is that this approach will likely be slower.
