from collections import Counter
import string


def letter_frequencies_normalized(word_list):
    # Flatten the list of words into a single string
    all_letters = ''.join(word_list).lower()

    # Filter only alphabetic characters
    filtered_letters = ''.join(filter(str.isalpha, all_letters))

    # Count frequencies of letters
    frequencies = Counter(filtered_letters)

    # Total number of letters
    total_letters = sum(frequencies.values())

    # Normalize frequencies
    normalized_frequencies = {letter: (frequencies[letter] / total_letters) * 100
                              for letter in string.ascii_lowercase if letter in frequencies}

    return normalized_frequencies

def substring_frequencies_normalized(possibilities, min_len=2, max_len=5):
    substring_counts = {}
    total_count = 0
    for word in possibilities:
        word_len = len(word)
        for n in range(min_len, min(max_len + 1, word_len + 1)):
            for i in range(word_len - n + 1):
                substr = word[i:i + n]
                substring_counts[substr] = substring_counts.get(substr, 0) + 1
                total_count += 1
    # Normalize the substring frequencies
    substring_freqs = {substr: count / total_count for substr, count in substring_counts.items()}
    return substring_freqs

if __name__ == '__main__':
    with open("FiveLetterWords.txt") as f:
        words = f.readlines()
        normalized_frequencies = letter_frequencies_normalized(words)
        print(normalized_frequencies)