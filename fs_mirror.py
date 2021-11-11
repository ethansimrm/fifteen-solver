"""
Loyd's Fifteen puzzle - solver and visualizer
Note that solved configuration has the blank (zero) tile in upper left
Use the arrows key to swap this tile with its neighbors
"""

import poc_fifteen_gui

class Puzzle:
    """
    Class representation for the Fifteen puzzle
    """

    def __init__(self, puzzle_height, puzzle_width, initial_grid=None):
        """
        Initialize puzzle with default height and width
        Returns a Puzzle object
        """
        self._height = puzzle_height
        self._width = puzzle_width
        self._grid = [[col + puzzle_width * row
                       for col in range(self._width)]
                      for row in range(self._height)]

        if initial_grid != None:
            for row in range(puzzle_height):
                for col in range(puzzle_width):
                    self._grid[row][col] = initial_grid[row][col]

    def __str__(self):
        """
        Generate string representaion for puzzle
        Returns a string
        """
        ans = ""
        for row in range(self._height):
            ans += str(self._grid[row])
            ans += "\n"
        return ans

    #####################################
    # GUI methods

    def get_height(self):
        """
        Getter for puzzle height
        Returns an integer
        """
        return self._height

    def get_width(self):
        """
        Getter for puzzle width
        Returns an integer
        """
        return self._width

    def get_number(self, row, col):
        """
        Getter for the number at tile position pos
        Returns an integer
        """
        return self._grid[row][col]

    def set_number(self, row, col, value):
        """
        Setter for the number at tile position pos
        """
        self._grid[row][col] = value

    def clone(self):
        """
        Make a copy of the puzzle to update during solving
        Returns a Puzzle object
        """
        new_puzzle = Puzzle(self._height, self._width, self._grid)
        return new_puzzle

    ########################################################
    # Core puzzle methods

    def current_position(self, solved_row, solved_col):
        """
        Locate the current position of the tile that will be at
        position (solved_row, solved_col) when the puzzle is solved
        Returns a tuple of two integers        
        """
        solved_value = (solved_col + self._width * solved_row)

        for row in range(self._height):
            for col in range(self._width):
                if self._grid[row][col] == solved_value:
                    return (row, col)
        assert False, "Value " + str(solved_value) + " not found"

    def update_puzzle(self, move_string):
        """
        Updates the puzzle state based on the provided move string
        """
        zero_row, zero_col = self.current_position(0, 0)
        for direction in move_string:
            if direction == "l":
                assert zero_col > 0, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row][zero_col - 1]
                self._grid[zero_row][zero_col - 1] = 0
                zero_col -= 1
            elif direction == "r":
                assert zero_col < self._width - 1, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row][zero_col + 1]
                self._grid[zero_row][zero_col + 1] = 0
                zero_col += 1
            elif direction == "u":
                assert zero_row > 0, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row - 1][zero_col]
                self._grid[zero_row - 1][zero_col] = 0
                zero_row -= 1
            elif direction == "d":
                assert zero_row < self._height - 1, "move off grid: " + direction
                self._grid[zero_row][zero_col] = self._grid[zero_row + 1][zero_col]
                self._grid[zero_row + 1][zero_col] = 0
                zero_row += 1
            else:
                assert False, "invalid direction: " + direction

    ##################################################################
    # Phase one methods

    def lower_row_invariant(self, target_row, target_col):
        """
        Check whether the puzzle satisfies the specified invariant
        at the given position in the bottom rows of the puzzle (target_row > 1)
        Returns a boolean
        """
        #Check if 0 is in correct place
        if self.get_number(target_row, target_col) != 0:
            return False
        #Check if all lower rows are arranged correctly
        for row_number in range(target_row + 1, self.get_height()):
            for col_number in range(0, self.get_width()):
                target_number = row_number * self.get_width() + col_number
                if self.get_number(row_number, col_number) != target_number:
                    return False
        #Check if everything to the right of 0 is correct
        for col_number in range(target_col + 1, self.get_width()):
            target_number = target_row * self.get_width() + col_number
            if self. get_number(target_row, col_number) != target_number:
                return False
        return True
    
    def transfer_zero(self, soln_string, vert_difference, hor_difference, vert_direction = "up", hor_direction = "none"):
        """
        This method will move the zero to where the target is.
        Returns string of moves by which it does so.
        """
        if vert_direction == "up":
            for dummy_step in range(vert_difference):
                soln_string += "u"
        elif vert_direction == "down":
            for dummy_step in range(vert_difference):
                soln_string += "d"
        if hor_direction == "right":
            for dummy_step in range(hor_difference):
                soln_string += "r"
        elif hor_direction == "left":
            for dummy_step in range(hor_difference):
                soln_string += "l"
        else:
            return soln_string
        return soln_string
    
    def zero_over_target(self, soln_string, vert_space):
        """
        This method will resolve situations where zero is directly over the target tile,
        and both these tiles are in the target column.
        
        It will shift the target tile downwards to its destination, 
        and place the zero on its left.
        
        Returns string of moves by which it does so.
        """
        for dummy_step in range(vert_space):
            soln_string += "lddru" #Move target tile directly downwards, one step per cycle
        #At this point, zero is at position (target_row + 1, target_col).
        #Thus, we only need to move it left and downwards to fulfill the final assertion.
        soln_string += "ld"
        return soln_string
    
    def position_tile(self, soln_string, dest_row, dest_col, target_tile_row, target_tile_col):
        """
        Moves target tile at (target_tile_row, target_tile_col)
        to (dest_row, dest_col). 
        The zero will be on its left, i.e. at (dest_row, dest_col - 1).
        
        Returns string of moves by which it does so.
        """
        vert_difference = dest_row - target_tile_row
        
        #Case 1: Target tile in same column as destination
        if target_tile_col == dest_col:
            soln_string = self.transfer_zero(soln_string, vert_difference, 0, "up", "none")
            #At this point, the target tile has moved one step down because zero has displaced it
            #Target tile at (target_tile_row + 1, target_tile_col)
            soln_string = self.zero_over_target(soln_string, vert_difference - 1)

        #Case 2: Target tile in a rightward column
        elif target_tile_col > dest_col:
            hor_difference = target_tile_col - dest_col
            soln_string = self.transfer_zero(soln_string, vert_difference, hor_difference, "up", "right")
            #At this point, the target tile has moved one step left because zero has displaced it
            #Target tile at (target_tile_row, target_tile_col - 1)
            if target_tile_row == 0:
                for dummy_step in range(hor_difference - 1):
                    soln_string += "dllur" #We can mutate row 1 however we like
                #At this point, the target tile has moved to a position directly above its destination
                #Target tile at (target_tile_row, target_col)
                #However, zero is still to its immediate right.
                soln_string += "dlu"
                #Now, zero is directly above the target tile, in the same column as its destination.
                soln_string = self.zero_over_target(soln_string, vert_difference - 1)
                
            else:
                for dummy_step in range(hor_difference - 1):
                    soln_string += "ulldr" #AMAP, minimise touching any row below 1.
                soln_string += "ul"
                #Now, zero is directly above the target tile, in the same column as its destination.
                soln_string = self.zero_over_target(soln_string, vert_difference)    
                
        #Case 3: Target tile in a leftward column
        elif target_tile_col < dest_col:
            hor_difference = dest_col - target_tile_col
            soln_string = self.transfer_zero(soln_string, vert_difference, hor_difference,"up", "left")
            #At this point, the target tile has moved one step right because zero has displaced it
            #Target tile at (target_tile_row, target_tile_col + 1)
            if target_tile_row == 0:
                for dummy_step in range(hor_difference - 1): #Move it right
                    soln_string += "drrul"
                soln_string += "dru"
                #Target tile at (target_tile_row + 1, target_col)
                #Now, zero is directly above the target tile, in the same column as its destination.
                soln_string = self.zero_over_target(soln_string, vert_difference - 1)
        
            else:
                for dummy_step in range(hor_difference - 1): #Avoid touching rows below 1 AMAP.
                    soln_string += "urrdl"
                #Special case: if target in same row - Note that hor_difference = 1 is accounted for.
                #Simply moving the zero left by 1 in transfer_zero will solve this,
                #And it passes through all conditions here.
                #At cycle's end, zero remains on target's left, so we don't need to extend string further.
                #We only extend when the target tile was not on the same row, as below:
                if target_tile_row != dest_row:
                    soln_string += "ur"
                    #Now, zero is directly above the target tile, in the same column as its destination.
                    soln_string = self.zero_over_target(soln_string, vert_difference)
        return soln_string
                
    def solve_interior_tile(self, target_row, target_col):
        """
        Place correct tile at target position
        Updates puzzle and returns a move string
        """
        #Sanity checks
        assert self.lower_row_invariant(target_row, target_col), "Cannot solve interior tile yet!"
        
        soln_string = ""
        
        #Create a clone of the puzzle to call solutions on
        test = self.clone() 
        
        #Find location of target tile and move it to destination
        (target_tile_row, target_tile_col) = test.current_position(target_row, target_col)         
        soln_string = self.position_tile(soln_string, target_row, target_col, target_tile_row, target_tile_col)
        
        #Final checks
        test.update_puzzle(soln_string)
        assert test.lower_row_invariant(target_row, target_col - 1), "Interior solution incorrect!"
        self.update_puzzle(soln_string)
        return soln_string

    def solve_col0_tile(self, target_row):
        """
        Solve tile in column zero on specified row (> 1)
        Updates puzzle and returns a move string
        """
        #Sanity checks
        assert target_row > 1, "Invalid Col0 input!"
        assert self.lower_row_invariant(target_row, 0), "Cannot solve for Col0 yet!"
        
        soln_string = ""
        
        #Create a clone of the puzzle to call solutions on
        test = self.clone()
        
        #Find location of target tile
        (target_tile_row, target_tile_col) = test.current_position(target_row, 0)
        
        ##At the resolution of each case, we want our target tile to be in its destination.
        ##We also want our zero tile to be at (target_row - 1, 1).
        #First edge case: target tile directly above zero tile
        if target_tile_row == target_row - 1 and target_tile_col == 0: 
            soln_string += "ur"        
        #Second edge case: target tile already at (target_row - 1, 1)
        elif target_tile_row == target_row - 1 and target_tile_col == 1:
            soln_string += "u"
            soln_string += "ruldrdlurdluurddlur"
            #The string above only applies when zero is at (target_row - 1, 0) and 
            #Target tile is at (target_row - 1, 1), hence the single "u".
        #Third case: target tile anywhere else
        else:
            soln_string += "ur"
            soln_string = self.position_tile(soln_string, target_row - 1, 1, target_tile_row, target_tile_col)
            soln_string += "ruldrdlurdluurddlur"
        #At this point, zero is at (target_row - 1, 1)
        soln_string = self.transfer_zero(soln_string, 0, self.get_width() - 2, "up", "right")    

        #Final checks
        test.update_puzzle(soln_string)
        assert test.lower_row_invariant(target_row - 1, self.get_width() - 1), "Col0 solution incorrect!"
        self.update_puzzle(soln_string)
        return soln_string

    #############################################################
    # Phase two methods

    def row0_invariant(self, target_col):
        """
        Check whether the puzzle satisfies the row zero invariant
        at the given column (col > 1)
        Returns a boolean
        """
        #Check if 0 is in correct place
        if self.get_number(0, target_col) != 0:
            return False
        #Check if all rows with n > 2 are arranged correctly
        for row_number in range(2, self.get_height()):
            for col_number in range(0, self.get_width()):
                target_number = row_number * self.get_width() + col_number
                if self.get_number(row_number, col_number) != target_number:
                    return False
        #Check if the columns to the right of the column containing 0 are correct
        for col_number in range(target_col + 1, self.get_width()):
            for row_number in range(2):
                target_number = row_number * self.get_width() + col_number
                if self.get_number(row_number, col_number) != target_number:
                    return False
        #Additionally, check if position (1, target_col) is solved
        target_number = 1 * self.get_width() + target_col
        if self.get_number(1, target_col) != target_number:
            return False
        return True

    def row1_invariant(self, target_col):
        """
        Check whether the puzzle satisfies the row one invariant
        at the given column (col > 1)
        Returns a boolean
        """
        #Check if 0 is in correct place
        if self.get_number(1, target_col) != 0:
            return False
        #Check if all rows with n > 2 are arranged correctly
        for row_number in range(2, self.get_height()):
            for col_number in range(0, self.get_width()):
                target_number = row_number * self.get_width() + col_number
                if self.get_number(row_number, col_number) != target_number:
                    return False
        #Check if the columns to the right of the column containing 0 are correct
        for col_number in range(target_col + 1, self.get_width()):
            for row_number in range(2):
                target_number = row_number * self.get_width() + col_number
                if self.get_number(row_number, col_number) != target_number:
                    return False
        return True

    def solve_row0_tile(self, target_col):
        """
        Solve the tile in row zero at the specified column
        Updates puzzle and returns a move string
        """
        #Sanity checks
        assert self.row0_invariant(target_col), "Cannot solve for Row0 yet!"
        
        soln_string = ""
        
        #Create a clone of the puzzle to call solutions on
        test = self.clone()
        
        #Find location of target tile
        (target_tile_row, target_tile_col) = test.current_position(0, target_col)
        
        ##At the resolution of each case, we want our target tile to be in its destination.
        ##We also want our zero tile to be at (1, target_col - 1).
        ##This is also its final position - we don't need to shift it left or right further.
        #First edge case: target tile left of zero tile
        if target_tile_row == 0 and target_tile_col == target_col - 1: 
            soln_string += "ld"        
        #Second edge case: target tile already in (1, target_col - 1)
        elif target_tile_row == 1 and target_tile_col == target_col - 1:
            soln_string += "lld"
            soln_string += "urdlurrdluldrruld" 
            #The string above only applies when zero is at (1, target_col - 2) and 
            #Target tile is at (1, target_col - 1), hence the "lld".
        #Third case: target tile anywhere else
        else:
            soln_string += "ld"
            soln_string = self.position_tile(soln_string, 1, target_col - 1, target_tile_row, target_tile_col)
            soln_string += "urdlurrdluldrruld"
        
        #Final checks
        test.update_puzzle(soln_string)
        assert test.row1_invariant(target_col - 1), "Row0 solution incorrect!"
        self.update_puzzle(soln_string)
        return soln_string

    def solve_row1_tile(self, target_col):
        """
        Solve the tile in row one at the specified column
        Updates puzzle and returns a move string
        """
        #Sanity checks
        assert self.row1_invariant(target_col), "Cannot solve for Row1 yet!"
        
        soln_string = ""
        
        #Create a clone of the puzzle to call solutions on
        test = self.clone()
        
        #Find the target tile and bring it over
        (target_tile_row, target_tile_col) = test.current_position(1, target_col)
        soln_string = self.position_tile(soln_string, 1, target_col, target_tile_row, target_tile_col)
        
        #At this point, 0 is to the left of the target, so we need to put it above the target
        soln_string += "ur"
        
        #Final checks
        test.update_puzzle(soln_string)
        assert test.row0_invariant(target_col), "Row1 solution incorrect!"
        self.update_puzzle(soln_string)
        return soln_string                        

    ###########################################################
    # Phase 3 methods

    def solve_2x2(self):
        """
        Solve the upper left 2x2 part of the puzzle
        Updates the puzzle and returns a move string
        """
        #Sanity checks
        assert self.row1_invariant(1), "Cannot solve 2x2 yet!"
        
        soln_string = ""
        
        #Create a clone of the puzzle to call solutions on
        test = self.clone()
        
        #Assuming the puzzle is solvable, our cases will depend on where the (1,1) tile is
        #Because solvable 2x2 puzzles are cyclic with period "druldruldrul", and knowing that
        #we solve these only when 0 is at (1,1), there are three possible positions:
        #dr(1)uldr(2)uldr(3)ul where zero is at (1,1). This is the basis of this approach.
        (target_tile_row, target_tile_col) = test.current_position(1, 1)
        if target_tile_row == 0 and target_tile_col == 1:
            soln_string += "ul"
        elif target_tile_row == 1 and target_tile_col == 0:
            soln_string += "lu"
        else:
            soln_string += "uldrul"
        
        #Final checks
        test.update_puzzle(soln_string)
        assert test.row0_invariant(0), "2x2 solution incorrect!"
        self.update_puzzle(soln_string)
        return soln_string   
        
    def solve_puzzle(self):
        """
        Generate a solution string for a puzzle
        Updates the puzzle and returns a move string
        """
        soln_string = ""
        #If puzzle is solved, that's that
        if self.row0_invariant(0):
            return soln_string
        #If not, let's find zero and shift it to the desired position
        for row in range(self._height):
            for col in range(self._width):
                if self._grid[row][col] == 0:
                    zero_row = row
                    zero_col = col
        vert_difference = self._height - 1 - zero_row
        hor_difference = self._width - 1 - zero_col
        soln_string += self.transfer_zero(soln_string, vert_difference, hor_difference, "down", "right")
        self.update_puzzle(soln_string)
        #At this point, zero should be at (height - 1, width - 1)
        for row in range(self.get_height() - 1, 1, -1):
            for col in range(self.get_width() - 1, -1, -1):
                if col == 0:
                    soln_string += self.solve_col0_tile(row)
                else:
                    soln_string += self.solve_interior_tile(row, col)
        for col in range(self.get_width() - 1, 1, -1):
            soln_string += self.solve_row1_tile(col)
            soln_string += self.solve_row0_tile(col)
        soln_string += self.solve_2x2()
        return soln_string   

# Start interactive simulation
poc_fifteen_gui.FifteenGUI(Puzzle(4, 4))

