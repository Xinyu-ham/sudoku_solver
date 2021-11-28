import numpy as np

class Grid():
    def __init__(self, array, parent=None):
        self.array = np.array(array)
        self.prev = np.zeros([9, 9])
        self.solved = False
        self.original = self.array
        self.solutions = []
        self.move_counter = 0
        self.parent = parent

    def add_solution(self, value, i, j):
        solution = Grid(self.array, parent=self)
        solution.fill_cell(value, i, j)
        self.solutions.append(solution)

    def get_row(self, row):
        return self.array[row]

    def get_col(self, col):
        return self.array.T[col]

    # split the 9x9 grid into 9 3x3 boxes
    # 0  1  2
    # 3  4  5
    # 6  7  8
    def get_box(self, index):
        r, c = index//3, index%3
        return self.array[r*3:r*3+3, c*3:c*3+3]

    # given a position (x, y) return box index
    def find_box_index(self, index):
        row = index[0]//3
        col = index[1]//3
        return row*3 + col

    # given a position (x, y) return a 3x3 box
    def get_box_from_cell(self, i, j):
        index = self.find_box_index([i, j])
        return self.get_box(index)


    def find_value(self, value):
        loc = np.argwhere(self.array==value)
        box = []
        for l in loc:
            box.append(self.find_box_index(l))
        box = np.array([box])
        return np.concatenate((loc, box.T), axis=1)


    def get_missing(self, subset):
        values = np.arange(1,10)
        subset = subset.flatten()
        return np.setdiff1d(values, subset)

    def no_change(self):
        return np.all(self.array==self.prev)

    def fill_cell(self, value, i, j):
        self.array[i][j] = value
        self.move_counter += 1



    def get_missing_values(self, row):
        missing = []
        for i in range(1, 10):
            if i not in row:
                missing.append(i)
        return np.array(missing)

    def get_missing_cells_line(self, row):
        missing = np.where(row==0)[0]
        return missing

    def get_missing_cells_box(self, box, box_index):
        missing = []
        for i, row in enumerate(box):
            row_no = 3*(box_index//3) + i
            missing_row = np.where(row==0)[0]
            for j in missing_row:
                col_no = 3*(box_index%3) + j
                missing.append([row_no, col_no])
        return missing


    def is_valid(self, value, i, j):
        if value in self.get_row(i):
            return False
        if value in self.get_col(j):
            return False
        box = self.get_box_from_cell(i, j)
        if value in box:
            return False
        return True

    def get_possible_values_in_cell(self, values, cell):
        possible_values = []
        i, j = cell
        for value in values:
            if self.is_valid(value, i, j):
                possible_values.append(value)
        return possible_values

    # for every number, check every 3x3 box to see if number can be filled there
    def step_one(self):
        self.prev = np.copy(self.array)
        possible_values = list(range(1, 10))
        for value in possible_values:
            # locations = self.find_value(value)
            for box in range(0, 9):
                box_values = self.get_box(box)
                if value not in box_values:
                    maybe_row = []
                    maybe_col = []
                    maybe_positions = []
                    for row in range(box // 3 * 3, box // 3 * 3 + 3):
                        if value not in self.get_row(row):
                            maybe_row.append(row)
                    for col in range(box % 3 * 3, box % 3 * 3 + 3):
                        if value not in self.get_col(col):
                            maybe_col.append(col)
                    for i in maybe_row:
                        for j in maybe_col:
                            if box_values[i % 3][j % 3] == 0:
                                maybe_positions.append([i, j])


                    if len(maybe_positions) == 1:
                        i, j = maybe_positions[0]
                        self.fill_cell(value, i ,j)
                    elif len(maybe_positions) == 0:
                        return 'conflict'
        return self.array

    # given a row, col, or box, if it contains 4 or less missing cells,
    # check if any of the missing cells can fit only one number
    def step_two(self):
        self.prev = np.copy(self.array)
        for row_no in range(9):
            row = self.get_row(row_no)
            missing_values = self.get_missing_values(row)
            if len(missing_values) > 4:
                continue
            missing_cells = self.get_missing_cells_line(row)
            missing_cells = [(row_no, col) for col in missing_cells]
            for cell in missing_cells:
                possible_values = self.get_possible_values_in_cell(missing_values, cell)
                if len(possible_values) == 0:
                    return 'conflict'
                elif len(possible_values) == 1:
                    value = possible_values[0]
                    i, j = cell
                    self.fill_cell(value, i, j)

        for col_no in range(9):
            col = self.get_col(col_no)
            missing_values = self.get_missing_values(col)
            if len(missing_values) > 4:
                continue
            missing_cells = self.get_missing_cells_line(col)
            missing_cells = [(row, col_no) for row in missing_cells]
            for cell in missing_cells:
                possible_values = self.get_possible_values_in_cell(missing_values, cell)
                if len(possible_values) == 0:
                    return 'conflict'
                elif len(possible_values) == 1:
                    value = possible_values[0]
                    i, j = cell
                    self.fill_cell(value, i, j)

        for box_no in range(9):
            box = self.get_box(box_no)
            missing_values = self.get_missing_values(box)
            if len(missing_values) > 4:
                continue
            missing_cells = self.get_missing_cells_box(box, box_no)
            for cell in missing_cells:
                possible_values = self.get_possible_values_in_cell(missing_values, cell)
                if len(possible_values) == 0:
                    return 'conflict'
                elif len(possible_values) == 1:
                    value = possible_values[0]
                    i, j = cell
                    self.fill_cell(value, i, j)

    def check_solve(self):
        return 0 not in self.array

    #basic solving step by repeating step 1 and 2
    # until no cell can be filled anymore
    def solve(self):
        self.solved = self.check_solve()
        if self.solved:
            return self.array
        else:
            nc1 = False
            nc2 = False
            while not (nc1 and nc2):
                state = self.step_one()
                if state == 'conflict':
                    return None
                nc1 = self.no_change()
                state = self.step_two()
                if state == 'conflict':
                    return None
                nc2 = self.no_change()
        return self.array

    # remove solution from parent if it reaches dead end (not necessary really)
    def remove_solution(self):
        self.parent.solutions.remove(self)
        return None

    # basically similar to step 1 and 2, given a col, row or box
    # find cells that has two possible values or a number with 2 possible locations
    # add each possible move as a possible solution
    def find_possible_solutions(self, choices):
        solutions = []
        missing_cell_per_row = 9 - np.count_nonzero(self.array, axis=1)
        for i, missing_cells in enumerate(missing_cell_per_row):
            if missing_cells == 2:
                row = self.get_row(i)
                missing_values = self.get_missing_values(row)
                j = np.where(row==0)[0][0]
                for value in missing_values:
                    solutions.append((value, i, j))

        missing_cell_per_col = 9 - np.count_nonzero(self.array, axis=0)
        for j, missing_cells in enumerate(missing_cell_per_col):
            if missing_cells == 2:
                col = self.get_col(j)
                missing_values = self.get_missing_values(col)
                i = np.where(col==0)[0][0]
                for value in missing_values:
                    solutions.append((value, i, j))

        for index in range(10):
            box = self.get_box(index)
            missing_cells = self.get_missing_cells_box(box, index)
            if len(missing_cells) == 2:
                missing_values = self.get_missing_values(box)
                for value in missing_values:
                    solutions.append((value, i, j))

        possible_values = list(range(1, 10))
        for value in possible_values:
            # locations = self.find_value(value)
            for box in range(0, 9):
                box_values = self.get_box(box)
                if value not in box_values:
                    maybe_row = []
                    maybe_col = []
                    maybe_positions = []
                    for row in range(box // 3 * 3, box // 3 * 3 + 3):
                        if value not in self.get_row(row):
                            maybe_row.append(row)
                    for col in range(box % 3 * 3, box % 3 * 3 + 3):
                        if value not in self.get_col(col):
                            maybe_col.append(col)
                    for i in maybe_row:
                        for j in maybe_col:
                            if box_values[i % 3][j % 3] == 0:
                                maybe_positions.append([i, j])
                    if len(maybe_positions) == choices:
                        for position in maybe_positions:
                            i, j = position
                            solutions.append((value, i, j))
        return solutions

    # create a new grid to be solved for each possible solution
    def add_solutions(self, solutions):
        for solution in solutions:
            value, i, j = solution
            self.add_solution(value, i, j)

    # solve each possible solution
    def evaluate_all_solutions(self, max_depth):
        for solution in self.solutions:
            solved = solution.recur_solve(max_depth=max_depth-1)
            if solved is not None:
                return solved

    # solve gird with step 1 & 2 until it stalemate
    # add possible move as a possible solution and recursively solve all
    def recur_solve(self, max_depth=5, choices=2):
        if max_depth == 0:
            return None
        solve_status = self.solve()

        if solve_status is None:
            return self.remove_solution()
        if 0 not in self.array:
            return self.array
        else:
            solutions = self.find_possible_solutions(choices)
            if not solutions:
                choices += 1
                solutions = self.find_possible_solutions(choices)
            self.add_solutions(solutions)
            return self.evaluate_all_solutions(max_depth)



if __name__ == '__main__':
    # g = Grid([
    #     [0, 6, 9, 0, 0, 2, 7, 0, 0],
    #     [0, 7, 0, 0, 5, 0, 0, 0, 9],
    #     [0, 0, 0, 4, 0, 0, 8, 0, 2],
    #     [0, 0, 3, 6, 0, 0, 0, 0, 0],
    #     [7, 0, 0, 0, 0, 0, 0, 0, 6],
    #     [0, 0, 0, 0, 0, 5, 4, 0, 0],
    #     [5, 0, 4, 0, 0, 8, 0, 0, 0],
    #     [2, 0, 0, 0, 3, 0, 0, 1, 0],
    #     [0, 0, 6, 9, 0, 0, 5, 7, 0],
    # ])
    g = Grid(
        [
            [0, 6, 0, 0, 0, 8, 3, 0, 7],
            [7, 1, 0, 0, 2, 0, 5, 0, 0],
            [0, 0, 0, 0, 1, 0, 2, 9, 0],
            [0, 0, 7, 0, 8, 4, 9, 0, 2],
            [3, 8, 0, 9, 0, 7, 4, 0, 1],
            [4, 0, 0, 2, 6, 0, 8, 0, 0],
            [0, 9, 6, 0, 7, 0, 0, 0, 0],
            [0, 0, 3, 0, 9, 0, 0, 0, 5],
            [1, 0, 5, 4, 0, 0, 6, 8, 0]
        ]
    )
    print(g.solve())