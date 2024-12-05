import random
from tqdm import tqdm
import concurrent.futures
import copy

# ANSI color codes
GREEN = '\033[32m'
YELLOW = '\033[33m'
RESET = '\033[0m'
BOLD = '\033[1m'


class WordleSolver:
    def __init__(self, words_file):
        with open(words_file) as f:
            self.words = [word.strip() for word in f.readlines() if len(word.strip()) == 5]
        self.reset()

    def reset(self):
        self.possibilities = self.words[:]
        self.includes = []
        self.excludes = []
        self.pos = {}
        self.not_pos = {}

    def compute_expected_remaining(self, guess):
        feedback_groups = {}
        total_possibilities = len(self.possibilities)

        for solution in self.possibilities:
            feedback = self.get_feedback(guess, solution)
            feedback_key = tuple(feedback)
            feedback_groups.setdefault(feedback_key, []).append(solution)

        expected_remaining = sum(
            (len(group) ** 2) / total_possibilities for group in feedback_groups.values()
        ) / total_possibilities

        return expected_remaining

    def get_feedback(self, guess, solution):
        if len(guess) != len(solution):
            raise ValueError(f"Length mismatch: guess '{guess}' and solution '{solution}' must be the same length.")
        feedback = []
        for i, char in enumerate(guess):
            if char == solution[i]:
                feedback.append(2)  # Green
            elif char in solution:
                feedback.append(1)  # Yellow
            else:
                feedback.append(0)  # Gray
        return feedback

    def update_possibilities(self):
        def is_possible(word):
            if any(char in self.excludes for char in word):
                return False
            if not all(char in word for char in self.includes):
                return False
            for idx, char in self.pos.items():
                if word[idx] != char:
                    return False
            for idx, chars in self.not_pos.items():
                if word[idx] in chars:
                    return False
            return True

        self.possibilities = [word for word in self.possibilities if is_possible(word)]

    def guess_next_word(self, iter_count, possible_guesses=None):
        if len(self.possibilities) == 1:
            return self.possibilities[0]

        potential_guesses = possible_guesses or self.words

        if iter_count == 1:
            # Implement Expectimax for the first word
            min_expected_remaining = float('inf')
            best_guess = None

            for guess in potential_guesses:
                expected_remaining = self.compute_expected_remaining(guess)
                if expected_remaining < min_expected_remaining:
                    min_expected_remaining = expected_remaining
                    best_guess = guess
                elif expected_remaining == min_expected_remaining:
                    # Tie-breaker: prefer guess in possibilities
                    if guess in self.possibilities:
                        best_guess = guess

            return best_guess or random.choice(self.possibilities)
        else:
            # Use existing strategy for subsequent guesses
            max_eliminations = -1
            best_guess = None

            for guess in self.possibilities:
                expected_eliminations = self.compute_expected_eliminations(guess)
                if expected_eliminations > max_eliminations:
                    max_eliminations = expected_eliminations
                    best_guess = guess

            return best_guess or random.choice(self.possibilities)

    def compute_expected_eliminations(self, guess):
        feedback_groups = {}
        total_possibilities = len(self.possibilities)

        for solution in self.possibilities:
            feedback = self.get_feedback(guess, solution)
            feedback_key = tuple(feedback)
            feedback_groups.setdefault(feedback_key, []).append(solution)

        expected_remaining = sum(
            (len(group) ** 2) / total_possibilities for group in feedback_groups.values()
        ) / total_possibilities

        expected_eliminations = total_possibilities - expected_remaining
        return expected_eliminations

    def process_feedback(self, guess, feedback):
        for i, val in enumerate(feedback):
            char = guess[i]
            if val == 0:
                if char not in self.includes:
                    self.excludes.append(char)
            elif val == 1:
                if char not in self.includes:
                    self.includes.append(char)
                self.not_pos.setdefault(i, []).append(char)
            elif val == 2:
                if char not in self.includes:
                    self.includes.append(char)
                self.pos[i] = char

    def format_guess(self, guess, feedback):
        formatted = ""
        for i, val in enumerate(feedback):
            char = guess[i]
            if val == 0:
                formatted += RESET + char
            elif val == 1:
                formatted += YELLOW + char
            elif val == 2:
                formatted += GREEN + char
        return BOLD + formatted + RESET


class WordleGame:
    def __init__(self, solver, auto_play=False, solution=None, verbose=True, initial_guess_options=None):
        self.solver = solver
        self.auto_play = auto_play
        self.solution = solution or random.choice(self.solver.words)
        self.iterations = 0
        self.verbose = verbose
        self.initial_guess_options = initial_guess_options or self.solver.words

    def provide_feedback(self, guess):
        feedback = []
        for i, char in enumerate(guess):
            if char == self.solution[i]:
                feedback.append(2)
            elif char in self.solution:
                feedback.append(1)
            else:
                feedback.append(0)
        return feedback

    def play(self):
        while True:
            self.iterations += 1
            guess = self.solver.guess_next_word(
                self.iterations,
                possible_guesses=self.initial_guess_options if self.iterations == 1 else None
            )

            if self.verbose:
                print(f"Iteration {self.iterations}: {guess} \nPossible words remaining: {len(self.solver.possibilities)}")

            if self.auto_play:
                feedback = self.provide_feedback(guess)
            else:
                feedback_input = input("Enter feedback (e.g., '2,1,0,0,1'): ")
                feedback = [int(x) for x in feedback_input.strip().split(',')]

            if feedback == [2, 2, 2, 2, 2]:
                if self.verbose:
                    print(f"Solution found in {self.iterations} iterations: {guess}")
                break

            if self.verbose:
                print(self.solver.format_guess(guess, feedback))
            self.solver.process_feedback(guess, feedback)
            self.solver.update_possibilities()


def run_test_word(word, words_file, initial_guess_options=None):
    solver = WordleSolver(words_file)
    solver.reset()
    game = WordleGame(
        solver,
        auto_play=True,
        solution=word,
        verbose=False,
        initial_guess_options=initial_guess_options
    )
    game.play()
    return game.iterations


def run_tests(test_words, words_file, initial_guess_options=None):
    iterations_list = []

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(
                run_test_word,
                word,
                words_file,
                initial_guess_options
            )
            for word in test_words
        ]
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Testing words"):
            iterations = future.result()
            iterations_list.append(iterations)

    average_iterations = sum(iterations_list) / len(iterations_list)
    print(f"\nAverage number of guesses: {average_iterations:.2f}")


def main_tests():
    words_file = "FiveLetterWords.txt"
    solver = WordleSolver(words_file)
    test_words = solver.words[:500]  # Adjust as needed
    initial_guess_options = ['raise', 'slate', 'crane', 'crate', 'slant']  # Example initial guesses
    run_tests(test_words, words_file, initial_guess_options)


if __name__ == "__main__":
    words_file = "FiveLetterWords.txt"
    solver = WordleSolver(words_file)
    solver.reset()
    initial_guess_options = ['cable']  # Your list of options
    game = WordleGame(
        solver,
        auto_play=True,
        solution='fella',
        initial_guess_options=initial_guess_options
    )
    game.play()