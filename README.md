# Sudoku Solver

A web-based visualization of the backtracking algorithm solving Sudoku puzzles in real-time. See it here: <https://sudoku-solver-sable.vercel.app/>

## Features

- Watch the solver work step-by-step with color-coded animations
- See constraint propagation (green) vs backtracking guesses (blue)
- Adjustable animation speed (slow to instant)
- Three difficulty levels via API Ninjas

## How It Works

The solver uses backtracking with constraint propagation. Cells with only one valid option are filled first, then the algorithm guesses and backtracks when it hits dead ends. Each step is recorded and animated on the frontend.

## Tech Stack

- Flask (backend)
- Vanilla JavaScript (frontend)
- Tailwind CSS
- API Ninjas (puzzle generation)
