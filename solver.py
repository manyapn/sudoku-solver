from typing import List, Set, Dict, Any
import copy

class SudokuSolver:

    def __init__(self, cell_options: List[str]) -> None:
        self.cell_options: List[str] = cell_options
        self.size: int = len(cell_options)
        self.sq_len: int = int(len(cell_options) ** 0.5)
        self.steps: List[Dict[str, Any]] = []  # Records animation steps

    def solve(self, grid: List[List[str]]) -> Dict[str, Any]:
        self.steps = []

        # Deep copy grid to avoid modifying original
        grid = copy.deepcopy(grid)

        # Generate grid locations, row sets, col sets, and square sets
        grid_locations: List[tuple] = self.gen_grid_locations(grid)
        grid_rows: List[Set] = self.gen_grid_rows(grid)
        grid_cols: List[Set] = self.gen_grid_cols(grid)
        grid_squares: List[List[Set]] = self.gen_grid_sq(grid)

        # Fill single possibility spaces (constraint propagation)
        self.fill_single_poss_spaces(grid, grid_locations, grid_rows, grid_cols, grid_squares)

        # Sort locations by number of possibilities (MRV heuristic for speed)
        grid_locations = self.sort_by_possibilities(grid, grid_locations, grid_rows, grid_cols, grid_squares)

        # Call recursive function
        solution = self.solve_recursive(grid, list(grid_locations), grid_rows, grid_cols, grid_squares)

        return {
            "solution": solution,
            "steps": self.steps
        }

    def sort_by_possibilities(self, grid, grid_locations, grid_rows, grid_cols, grid_squares) -> List[tuple]:
        def count_possibilities(loc):
            chars = self.gen_safe_chars(grid, loc, grid_rows, grid_cols, grid_squares)
            return len(chars) if chars else 0

        return sorted(grid_locations, key=count_possibilities, reverse=True)

    def gen_grid_locations(self, grid: List[List[str]]) -> List[tuple]:
        grid_locations: List[tuple] = []
        for i in range(self.size):
            for j in range(self.size):
                if grid[i][j] is None:
                    grid_locations.append((i, j))
        return grid_locations

    def gen_grid_rows(self, grid: List[List[str]]) -> List[Set]:
        grid_rows: List[Set] = []
        for row in grid:
            row_set: Set = set(row)
            row_set.discard(None)
            grid_rows.append(row_set)
        return grid_rows

    def gen_grid_cols(self, grid: List[List[str]]) -> List[Set]:
        grid_cols: List[Set] = []
        for i in range(self.size):
            temp_col_set: Set = set()
            for j in range(self.size):
                if grid[j][i] is not None:
                    temp_col_set.add(grid[j][i])
            grid_cols.append(temp_col_set)
        return grid_cols

    def gen_grid_sq(self, grid: List[List[str]]) -> List[List[Set]]:
        grid_squares: List[List[Set]] = [[None] * self.sq_len for _ in range(self.sq_len)]

        for i in range(self.sq_len):
            for j in range(self.sq_len):
                sq_row: int = i
                sq_col: int = j

                temp_sq_set: Set = set()
                for k in range(sq_row * self.sq_len, (1 + sq_row) * self.sq_len):
                    for l in range(sq_col * self.sq_len, (1 + sq_col) * self.sq_len):
                        if grid[k][l] is not None:
                            temp_sq_set.add(grid[k][l])

                grid_squares[sq_row][sq_col] = temp_sq_set

        return grid_squares

    def fill_single_poss_spaces(self, grid: List[List[str]], grid_locations: List,
                                 grid_rows: List[Set], grid_cols: List[Set],
                                 grid_squares: List[List[Set]]) -> None:
        changed = True
        while changed:
            changed = False
            singleposindex: List[int] = []

            for i in range(len(grid_locations)):
                location = grid_locations[i]
                safe_chars: Set = self.gen_safe_chars(grid, location, grid_rows, grid_cols, grid_squares)

                if safe_chars and len(safe_chars) == 1:
                    safe_char = safe_chars.pop()
                    grid[location[0]][location[1]] = safe_char

                    # Record step for animation
                    self.steps.append({
                        "action": "place",
                        "row": location[0],
                        "col": location[1],
                        "value": safe_char,
                        "type": "propagation"
                    })

                    # Add to row, col, and square sets
                    grid_rows[location[0]].add(safe_char)
                    grid_cols[location[1]].add(safe_char)

                    sq_row: int = location[0] // self.sq_len
                    sq_col: int = location[1] // self.sq_len
                    grid_squares[sq_row][sq_col].add(safe_char)

                    singleposindex.append(i)
                    changed = True

            # Remove filled locations from grid_locations (in reverse order)
            for i in range(len(singleposindex) - 1, -1, -1):
                grid_locations.pop(singleposindex[i])

    def gen_safe_chars(self, grid: List[List[str]], grid_loc: tuple,
                       grid_rows: List[Set], grid_cols: List[Set],
                       grid_squares: List[List[Set]]) -> Set[str]:
        ops: Set[str] = set(self.cell_options)

        # Remove items in row
        ops = ops.difference(grid_rows[grid_loc[0]])

        # Remove items in col
        ops = ops.difference(grid_cols[grid_loc[1]])

        # Remove items in square
        sq_row: int = grid_loc[0] // self.sq_len
        sq_col: int = grid_loc[1] // self.sq_len
        sq_set = grid_squares[sq_row][sq_col]
        ops = ops.difference(sq_set)

        return ops if len(ops) > 0 else None

    def solve_recursive(self, grid: List[List[str]], grid_locations: List,
                        grid_rows: List[Set], grid_cols: List[Set],
                        grid_squares: List[List[Set]]) -> List[List[str]]:
        if len(grid_locations) == 0:
            return grid

        location = grid_locations.pop()
        chars: Set[str] = self.gen_safe_chars(grid, location, grid_rows, grid_cols, grid_squares)

        if chars is None:
            return None

        for char in chars:
            # Place the character
            grid[location[0]][location[1]] = char

            # Record step for animation
            self.steps.append({
                "action": "place",
                "row": location[0],
                "col": location[1],
                "value": char,
                "type": "guess"
            })

            # Add to row, col, and square sets
            grid_rows[location[0]].add(char)
            grid_cols[location[1]].add(char)

            sq_row: int = location[0] // self.sq_len
            sq_col: int = location[1] // self.sq_len
            grid_squares[sq_row][sq_col].add(char)

            # Explore
            result = self.solve_recursive(grid, list(grid_locations), grid_rows, grid_cols, grid_squares)
            if result is not None:
                return result

            # Backtrack - record step for animation
            self.steps.append({
                "action": "backtrack",
                "row": location[0],
                "col": location[1],
                "value": None,
                "type": "backtrack"
            })

            # Remove from row, col, and square sets
            grid_rows[location[0]].remove(char)
            grid_cols[location[1]].remove(char)
            grid_squares[sq_row][sq_col].remove(char)

        # Unchoose
        grid[location[0]][location[1]] = None
        grid_locations.append(location)

        return None


def parse_puzzle_string(puzzle_str: str) -> List[List[str]]:

    grid = []
    for i in range(9):
        row = []
        for j in range(9):
            char = puzzle_str[i * 9 + j]
            row.append(None if char == '0' else char)
        grid.append(row)
    return grid


def solve_puzzle(puzzle_str: str) -> Dict[str, Any]:

    grid = parse_puzzle_string(puzzle_str)
    cell_options = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]

    solver = SudokuSolver(cell_options)
    result = solver.solve(grid)

    return result
