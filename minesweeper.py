import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # iterate over cells in sentence 
        if len(self.cells) == self.count:
            return set(self.cells)
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
       # iterate over cells in sentence
        if self.count  == 0:
            return set(self.cells)
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            # remove mine from sentence
            self.cells.remove(cell)
            # decrease count by 1
            self.count -= 1
            return None

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            # remove safe cell from sentence --> count does not need to be decreased because ther are no mines on safe cells
            self.cells.remove(cell)
            return None


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def neighboring_cells(self, cell):
        """
        Computes all neighboring cells for any cell
        """
        mines = 0
        i, j = cell
        neighbors = set()
        for row in range(i-1, i+2):
            # check if row is out of range of the board
            for col in range(j-1, j+2):
                    # check if column is out of range of the board or cell itself
                    if ((col >= 0 and col < self.width) 
                                        and ((row,col) != cell) 
                                        and (row >= 0 and row < self.height) 
                                        and ((row,col) is not self.moves_made)):
                        # if (row,col) is inside of board and not cell itself --> add it to neighbors list
                        if (row,col) in self.mines:
                            mines +=1
                        elif (row,col) in self.safes:
                            continue
                        else:
                            neighbors.add((row,col))
        return neighbors, mines

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1
        self.moves_made.add(cell)
        # 2
        self.safes.add(cell)
        # 3
        # get neighbors
        neighbors = self.neighboring_cells(cell)[0]
        detected_mines = self.neighboring_cells(cell)[1]
        # adjust count
        count -= detected_mines
        # create new sentence from neighbor cells and count
        new_sentence = Sentence(neighbors,count)
        # add new sentence to knowledge base
        if new_sentence not in self.knowledge: #not in 
            self.knowledge.append(new_sentence)

        # 4
        # iterate over sentences
        for sentence in self.knowledge:
            # get list of known safes in sentence
            known_safes = sentence.known_safes()
            # add known_safes to safes
            for known_safe in known_safes:
                self.mark_safe(known_safe)
            # get list of known mines
            known_mines = sentence.known_mines()
            # add known mines to mines
            for known_mine in known_mines:
                self.mark_mine(known_mine)


        # 5
        # iterate over sentences in knowledge bast
        known_sentences = copy.deepcopy(self.knowledge)
        # iterate over known sentences
        for sentence1 in known_sentences:
            # delete sentence selected to avoid infinite loop
            known_sentences.remove(sentence1)
            # iterate over remaining sentences
            for sentence2 in known_sentences:
                # check which of the two sets has a greater length
                if ((len(sentence2.cells) < len(sentence1.cells)) 
                                    and len(sentence1.cells) != 0 
                                    and len(sentence2.cells) != 0):
                    subset = sentence2.cells
                    bigset = sentence1.cells
                    diff_count = sentence1.count - sentence2.count
                # if set are the same --> continue
                elif len(sentence2.cells) == len(sentence1.cells):
                    continue
                elif ((len(sentence2.cells) > len(sentence1.cells)) 
                                    and len(sentence1.cells) != 0 
                                    and len(sentence2.cells) != 0):
                    subset = sentence1.cells
                    bigset = sentence2.cells
                    diff_count = sentence2.count - sentence1.count
                # if none of the above apply continue --> to not get an infinite loop
                else:
                    continue
                 # check if new sentence is subset of KB-sentence or voce versa
                if subset <= bigset:
                    # get difference subset between the two 
                    diff_set = bigset - subset
                    # check if there is just one extra field in KB-sentence
                    if len(diff_set) == 1:
                        # check if diff_set is known mine or safe 
                        if diff_count == 0:
                            new_safe = diff_set.pop()
                            # add to known safe cells
                            self.mark_safe(new_safe)
                        elif diff_count == 1:
                            new_mine = diff_set.pop()
                            # add to known mines
                            self.mark_mine(new_mine)
                    else:
                        # add new subset knowledge to knowledge base
                        self.knowledge.append(Sentence(diff_set, diff_count))
        # # raise NotImplementedError

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # get first safe move that has not been made yet
        print(f'{len(self.safes - self.moves_made)} known unused safes')
        print(f'{len(self.mines)} detected mines:\n{list(self.mines)}')
        for move in self.safes:
            # check for move that has not been made yet
            if move in self.moves_made:
                continue
            else:
                safe_move = move
                # add to made moves
                self.moves_made.add(safe_move)
                print(f'Move made:{safe_move}')
                # if a safe move that has not been made is found --> break out of loops
                return safe_move
        return None
    

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        potential_move = []
        # iterate over all board cells and add to board
        board = []
        for row in range(self.height):
            for col in range(self.width):
                board.append((row,col))
        for pot_cell in board:
            # check they have not been chosen and are no mines
            if (pot_cell not in self.mines) and (pot_cell not in self.moves_made):
                potential_move.append(pot_cell)
        if len(potential_move) == 0:
            print(f'\nGame finished! Reset board to play another game.')
        else:
            # chose truly random move from all potential moves (not just the first or last potential move in the list)
            random_move = random.choice(potential_move)
            # add to made moves
            self.moves_made.add(random_move)
            print(f'Move made:{random_move}')
            return random_move
