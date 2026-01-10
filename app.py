import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import requests
from solver import solve_puzzle

load_dotenv()  # Load .env file

app = Flask(__name__)
CORS(app)

# Load API key from environment variable
API_NINJAS_KEY = os.environ.get("API_NINJAS_KEY")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/puzzle/<difficulty>/<size>")
def get_puzzle(difficulty, size):
    """
    Fetch a puzzle from API Ninjas.
    """
    import random
    try:
        seed = random.randint(1, 100000)
        response = requests.get(
            f"https://api.api-ninjas.com/v1/sudokugenerate?width={size}&height={size}&seed={seed}&difficulty={difficulty}",
            headers={"X-Api-Key": API_NINJAS_KEY}
        )

        if response.status_code == 200:
            data = response.json()
            # Convert 2D array to string (null -> "0", numbers -> str)
            puzzle_2d = data["puzzle"]
            puzzle_str = ""
            for row in puzzle_2d:
                for cell in row:
                    puzzle_str += "0" if cell is None else str(cell)
            return jsonify({
                "success": True,
                "puzzle": puzzle_str,
                "difficulty": difficulty,
                "size": size
            })
        else:
            return jsonify({
                "success": False,
                "error": f"API returned status {response.status_code}"
            }), 500

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/solve", methods=["POST"])
def solve():
    """
    Solve a puzzle and return solution with animation steps.
    Expects JSON: {"puzzle": "puzzle_string"}
    """
    try:
        data = request.get_json()
        puzzle_str = data.get("puzzle")

        if not puzzle_str or len(puzzle_str) != 81:
            return jsonify({
                "success": False,
                "error": "Invalid puzzle format"
            }), 400

        result = solve_puzzle(puzzle_str)

        if result["solution"] is None:
            return jsonify({
                "success": False,
                "error": "No solution found"
            }), 400

        return jsonify({
            "success": True,
            "solution": result["solution"],
            "steps": result["steps"],
            "step_count": len(result["steps"])
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
