"""
xword_gen.py
Crossword puzzle generator. Originally for lightning round education games for Moonlight Focus.
Nate Cadicamo
5 August 2024

Algorithm:
    0. input: list of words
    1. sort words by length, longest to shortest
    2. create an empty square grid of at least size of longest word
    3. place longest word first in pseudo-random position
    4. choose next longest word and find a valid fit, or no fit; repeat until no more words
    5. if not all words were placed, try again for 10 total times (empirically works sometimes)
    6. if still not all words were placed, repeat 2 - 5 with grid size + 1
    7. maintain dict of valid candidate grids, return grid of highest density

Notes: empirically, this algorithm generates a crossword in less than a second. It produces a large number 
of candidate crosswords and selects the one with highest density, which we assume to be a more desirable 
crossword puzzle. Runtime is approximately quadratic in number of grid positions, linear in number of words.
Also note that this can easily be adapted to build a word search puzzle.
"""

import random
import time


def init_grid(size: int):
    """
    Initializes and returns an empty grid of specified size.
    """
    return [[' ' for _ in range(size)] for _ in range(size)]


def build_crossword(grid, wordlist_sorted):
    """
    Builds crossword on input grid of given size from a sorted list of words according to specified algorithm.
    Returns crossword as grid and placements dictionary.
    """

    # track word placement {word number : [word, starting pos (row, col), direction 'H' or 'V']}
    placements = {}

    # place the first word at a random valid position
    first = wordlist_sorted[0]
    grid, placements = place_first(grid, first, placements)

    # loop over remaining words
    words = wordlist_sorted[1:]
    for i in range(len(words)):
        word = words[i]

        # find best placement on grid and place it there
        row, col, letter_idx, direction = find_best_placement(word, grid, wordlist_sorted)
        if row or col or letter_idx or direction:
            grid, placements = place_word(grid, word, letter_idx, row, col, direction, placements, i + 2)
        
    # the grid is now built
    return grid, placements


def place_first(grid, first: str, placements):
    """
    Helper function to place the first word on grid pseudorandomly.
    """

    # track the size of grid for ease
    size = len(grid)

    # choose a direction and starting position at random and place word there
    direction = random.choice(['V', 'H'])
    if direction == 'H':
        row = random.randint(0, size - 1)
        return place_word(grid, first, 0, row, 0, 'H', placements, 1)
    elif direction == 'V':
        col = random.randint(0, size - 1)
        return place_word(grid, first, 0, 0, col, 'V', placements, 1)


def place_word(grid, word: str, letter_idx: int, row, col, direction, placements, wordnum):
    """
    Helper function to place word on grid at specified row, col, adjusted for letter index, and in given direction.
    Also updates placement dictionary with word number in list of original input words.
    """
    if direction == 'H':
        placements[wordnum] = [word, (row, col - letter_idx), 'H']
        for i in range(len(word)):
            grid[row][col - letter_idx + i] = word[i]
    elif direction == 'V':
        placements[wordnum] = [word, (row - letter_idx, col), 'V']
        for i in range(len(word)):
            grid[row - letter_idx + i][col] = word[i]
                
    return grid, placements


def find_best_placement(word: str, grid, wordlist_sorted):
    """
    Finds a best (dense) placement for a word on the grid.
    Tracks a best score and position based on is_valid_placement return value for count of letter overlaps.
    Placement with most valid letter overlaps will win.
    """

    # track candidate positions
    best_score = -1 
    best_position = None

    # loop over each letter in word
    for i in range(len(word)):
        letter = word[i]

        # loop over each spot in grid
        size = len(grid)
        for row in range(size):
            for col in range(size):
                
                # only proceed if letters overlap
                if letter == grid[row][col]:

                    # check placement validity, only save placement if denser than current                
                    h_valid = is_valid_placement(grid, word, i, row, col, 'H', wordlist_sorted)
                    if h_valid:
                        if h_valid[1] >= best_score:
                            best_score = h_valid[1]
                            best_position = (row, col, i, 'H')
                    v_valid = is_valid_placement(grid, word, i, row, col, 'V', wordlist_sorted)
                    if v_valid:
                        if v_valid[1] >= best_score:
                            best_score = v_valid[1]
                            best_position = (row, col, i, 'V')
                  
    # if never found a position, word unusable on current grid size; will build bigger grid in generate()
    if not best_position:
        return False, False, False, False
    else:
        # print(best_score)
        return best_position

                   
def is_valid_placement(grid, word: str, letter_idx: int, row, col, direction, wordlist_sorted):
    """
    Helper function for find_best_placement to check if a potential placement is valid.
    Investigates placement of word on grid at row, col, letter index and direction, returns True only if valid.
    Also tracks number of overlaps for find_best_placement to maximize for dense crosswords.
    """

    # save grid size for ease of use
    size = len(grid)

    # track number of overlaps
    num_overlaps = 0

    # check horizontal case
    if direction == 'H':

        # check left bound and right bound
        if col - letter_idx < 0 or col - letter_idx + len(word) > size:
            return False

        # check upper border of word (must be blank or at edge)
        if col - letter_idx > 0 and grid[row][col - letter_idx - 1] != ' ':
            return False
        
        # check lower border of word (must be blank or at edge)
        if col - letter_idx + len(word) < size and grid[row][col - letter_idx + len(word)] != ' ':
            return False

        # loop over letters in word to check letter placement
        for i in range(len(word)):

            # check if there is a different letter at this spot already
            if grid[row][col - letter_idx + i] not in (' ', word[i]):
                return False
            
            # track number of overlaps
            if grid[row][col - letter_idx + i] == word[i]:
                num_overlaps += 1
            
            # check for adjacent words in the row above
            if row > 0 and grid[row - 1][col - letter_idx + i] != ' ' and i != letter_idx:
                if is_adjacent_word(grid, row - 1, col - letter_idx + i, 'V', wordlist_sorted):
                    num_overlaps += 1
                else:
                    return False
            
            # check for adjacent words in the row below
            if row < size - 1 and grid[row + 1][col - letter_idx + i] != ' ' and i != letter_idx:
                if is_adjacent_word(grid, row + 1, col - letter_idx + i, 'V', wordlist_sorted):
                    num_overlaps += 1
                else:
                    return False
        
     # check vertical case
    elif direction == 'V':

        # check upper bound and lower bound
        if row - letter_idx < 0 or row - letter_idx + len(word) > size:
            return False
        
         # check left border of word (must be blank or at edge)
        if row - letter_idx > 0 and grid[row - letter_idx - 1][col] != ' ':
            return False
        
        # check right border of word (must be blank or at edge)
        if row - letter_idx + len(word) < size and grid[row - letter_idx + len(word)][col] != ' ':
            return False

        # loop over letters in word to check letter placement
        for i in range(len(word)):

            # check if there is a different letter at this spot already
            if grid[row - letter_idx + i][col] not in (' ', word[i]):
                return False
            
            # track number of overlaps
            if grid[row - letter_idx + i][col] == word[i]:
                num_overlaps += 1
            
            # check for adjacent words in the col to left
            if col > 0 and grid[row - letter_idx + i][col - 1] != ' ' and i != letter_idx:
                if is_adjacent_word(grid, row - letter_idx + i, col - 1, 'H', wordlist_sorted):
                    num_overlaps += 1
                else:
                    return False
            
            # check for adjacent words in the col to right
            if col < size - 1 and grid[row - letter_idx + i][col + 1] != ' ' and i != letter_idx:
                if is_adjacent_word(grid, row - letter_idx + i, col + 1, 'H', wordlist_sorted):
                    num_overlaps += 1
                else:
                    return False
                           
        
    # if all these tests pass, it's valid
    return True, num_overlaps


def is_adjacent_word(grid, row, col, direction, wordlist_sorted):
    """
    Helper function for is_valid_placement, called when letter detected at given row, col.
    Check if letters detected there extend to form a valid word from wordlist in given direction. 
    """

    # save max searching length
    max_len = len(max(wordlist_sorted, key=len))

    # check vertical case
    if direction == 'V':

        # build up a candidate word starting at the detected letter
        word = grid[row][col]

        # look up
        for i in range(1, max_len):            
            # check boundary 
            if row - i >= 0:
                # check end of word
                if grid[row - i][col] == ' ':
                    break
                # build up beginning of word
                word = grid[row - i][col] + word
            else:
                break

        # look down
        for i in range(1, max_len):            
            # check boundary 
            if row + i < len(grid):
                # check end of word
                if grid[row + i][col] == ' ' or row + i == len(grid):
                    break
                # build up end of word
                word = word + grid[row + i][col]
            else:
                break

        # word is built up, so check it out
        if word in wordlist_sorted:
            # print("found an adjacent word")
            return True
        else:
            # print(f"found a NON-word: {word}")
            return False

    # check horizontal case
    if direction == 'H':

        # build up a candidate word starting at the detected letter
        word = grid[row][col]

        # look up
        for i in range(1, max_len):            
            # check boundary 
            if col - i >= 0:
                # check end of word
                if grid[row][col - i] == ' ':
                    break
                # build up beginning of word
                word = grid[row][col - i] + word
            else:
                break

        # look down
        for i in range(1, max_len):            
            # check boundary 
            if col + i < len(grid):
                # check end of word
                if grid[row][col + i] == ' ' or col + i == len(grid):
                    break
                # build up end of word
                word = word + grid[row][col + i]
            else:
                break

        # word is built up, so check it out
        if word in wordlist_sorted:
            # print("found an adjacent word")
            return True
        else:
            # print(f"found a NON-word: {word}")
            return False
        

def print_grid(grid):
    """
    Printing helper function to display grid in terminal.
    """
    for row in grid:
        print(' | '.join(row))


def count_blanks(grid):
    """
    Helper function to count blanks in grid as measure of crossword density.
    """
    count = 0
    for row in range(len(grid)):
        for col in range(len(grid)):
            if grid[row][col] == ' ':
                count += 1
    return count


def generate(wordlist, verbose=False):
    """
    Generating function, callable externally.
    Input: wordlist as list of strings.
    Output: crossword as grid, placements dictionary.
    """

    # time the generation
    start = time.time()

    # sort the wordlist
    wordlist_sorted = sorted(wordlist, key=len, reverse=True)

    # initialize a grid size of minimum size, which is len of max len word
    grid_size = len(wordlist_sorted[0])

    # logic to ensure we always get all the words with the minimum size grid
    max_iter = 100
    candidate_grids = {}
    for i in range(max_iter):
        grid = init_grid(grid_size)
        crossword, placements = build_crossword(grid, wordlist_sorted)

        # if this is a valid crossword, store it in consideration
        if len(placements.keys()) == len(wordlist_sorted):
            candidate_grids[count_blanks(crossword)] = (crossword, placements)
        else:
            # try at least 5 times before upping grid size (empirically relevant)
            if i % 5 == 0:
                grid_size += 1

    # error check and find the min size grid as the winner
    if candidate_grids:
        crossword, placements = candidate_grids[sorted(candidate_grids.keys())[0]]
    else:
        print("A valid crossword is not possible for given wordlist.")
        return 
        
    # display if we want to inpsect
    if verbose:
        print_grid(crossword)
        print(placements)
        print(f"Total generation time: {time.time() - start} seconds.")

    # return crossword and data to caller 
    return crossword, placements


# toy default words as an example to work with in dev
DEFAULT_WORDS = [
    'photosynthesis',
    'chloroplasts',
    'thylakoid',
    'membranes',
    'solar',
    'energy',
    'atp',
    'nadph',
    'glucose',
    'co2',
    'mitochondria',
    'ribosome',
    'cytoplasm',
    'nucleus',
    'organelle',
    'vacuole',
    'lysosome',
    'cellulose',
    'enzymes',
    'osmosis',
    'diffusion',
    'chlorophyll',
    'respiration',
    'transcription',
    'translation',
    'mutation',
    'genome',
    'allele',
    'meiosis',
    'fertilization',
    'chromosome',
    'cytokinesis',
    'eukaryote',
    'prokaryote',
    'plasma',
    'flagella',
    'cilia',
    'cytoskeleton',
    'centrosome',
    'centriole',
    'peroxisome',
    'endocytosis',
    'exocytosis',
    'glycolysis',
    'krebs',
    'electron',
    'phospholipid',
    'biomolecule',
    'macromolecule'
]


# example call
generate(DEFAULT_WORDS, verbose=True)
generate(["cat", "tiger", "bat", "whale"], verbose=True)

