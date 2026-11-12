"""
Bincom ICT Solutions - Python Basic Developer Test
Python 3 solution.

Place python_class_question.html in the same folder as this script, then run:
    python bincom_python_test.py

Optional PostgreSQL configuration (environment variables):
    DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

Install the optional PostgreSQL driver with:
    pip install "psycopg[binary]"

Data note:
The supplied HTML contains "ARSH" and "BLEW". The normalization map below
treats ARSH as ASH and BLEW as BLUE. Change/remove these mappings if the
recruiter intended the source entries to be kept literally.
"""

from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import os
import random
import statistics


HTML_FILE = Path(__file__).with_name("python_class_question.html")

# Explicitly documented assumptions about apparent spelling errors.
COLOUR_CORRECTIONS = {
    "ARSH": "ASH",
    "BLEW": "BLUE",
}


class ColourTableParser(HTMLParser):
    """Extract day/colour rows from the HTML table."""

    def __init__(self):
        super().__init__()
        self.rows = []
        self.current_row = []
        self.current_cell = ""
        self.in_cell = False

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self.current_row = []
        elif tag == "td":
            self.current_cell = ""
            self.in_cell = True

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += data

    def handle_endtag(self, tag):
        if tag == "td":
            self.current_row.append(self.current_cell.strip())
            self.in_cell = False
        elif tag == "tr" and self.current_row:
            self.rows.append(self.current_row)


def extract_colours(html_path):
    """Read the supplied HTML file and return all colour entries."""
    if not html_path.exists():
        raise FileNotFoundError(
            f"Could not find {html_path.name}. Put it beside this Python file."
        )

    html = html_path.read_text(encoding="utf-8")
    parser = ColourTableParser()
    parser.feed(html)

    all_colours = []
    for row in parser.rows:
        if len(row) == 2 and row[0].strip().upper() in {
            "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"
        }:
            day_colours = row[1].split(",")
            for item in day_colours:
                original = item.strip().upper()
                if original:
                    corrected = COLOUR_CORRECTIONS.get(original, original)
                    all_colours.append(corrected)

    if not all_colours:
        raise ValueError("No colour entries were found in the HTML table.")

    return all_colours


def analyse_colours(colours):
    """Print frequency and descriptive statistics for the colour data."""
    frequencies = Counter(colours)
    total_entries = len(colours)
    distinct_colours = len(frequencies)
    frequency_values = list(frequencies.values())

    print("\nBINCOM STAFF COLOUR ANALYSIS")
    print("=" * 38)
    print(f"Total colour entries: {total_entries}")
    print(f"Number of distinct colours: {distinct_colours}")

    print("\nColour frequencies:")
    for colour, count in sorted(
        frequencies.items(), key=lambda item: (-item[1], item[0])
    ):
        print(f"{colour.title():<12} {count}")

    # Mode: the colour (or colours) with the highest frequency.
    highest_count = max(frequencies.values())
    modes = [
        colour for colour, count in frequencies.items()
        if count == highest_count
    ]
    print("\n1. Most frequently worn colour (mode):")
    print(f"{', '.join(sorted(modes)).title()} ({highest_count} times)")

    # Mean and median are meaningful for the numerical frequency values,
    # not directly for nominal colour names.
    mean_frequency = statistics.mean(frequency_values)
    median_frequency = statistics.median(frequency_values)
    variance_frequency = statistics.pvariance(frequency_values)

    print("\n2. Mean frequency per distinct colour:")
    print(f"{mean_frequency:.2f}")

    # If an answer requires one representative colour, choose the colour
    # whose frequency is closest to the mean frequency. This is NOT a
    # mathematical mean colour; it is an explicitly stated interpretation.
    closest_to_mean = min(
        frequencies,
        key=lambda colour: (abs(frequencies[colour] - mean_frequency), colour)
    )
    print(
        "Colour closest to the mean frequency "
        f"(interpretation only): {closest_to_mean.title()} "
        f"({frequencies[closest_to_mean]} times)"
    )

    print("\n3. Median frequency:")
    print(f"{median_frequency:g}")
    print(
        "A median colour is not uniquely defined because colour names "
        "have no natural numerical order."
    )

    print("\n4. Bonus - Population variance of colour frequencies:")
    print(f"{variance_frequency:.4f}")

    print("\n5. Bonus - Probability of randomly selecting red:")
    red_count = frequencies.get("RED", 0)
    probability = red_count / total_entries
    print(f"{red_count}/{total_entries} = {probability:.4%}")

    return frequencies


def save_frequencies_to_postgresql(frequencies):
    """
    Save colour frequencies to PostgreSQL.
    Database settings are read from environment variables.
    """
    required_settings = ["DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST"]
    missing = [name for name in required_settings if not os.getenv(name)]

    if missing:
        print(
            "\n6. PostgreSQL: skipped because these environment variables "
            f"are not configured: {', '.join(missing)}"
        )
        return

    try:
        import psycopg

        connection = psycopg.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT", "5432"),
        )

        with connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS bincom_colour_frequencies (
                        colour VARCHAR(50) PRIMARY KEY,
                        frequency INTEGER NOT NULL CHECK (frequency >= 0)
                    )
                """)

                for colour, frequency in frequencies.items():
                    cursor.execute(
                        """
                        INSERT INTO bincom_colour_frequencies (colour, frequency)
                        VALUES (%s, %s)
                        ON CONFLICT (colour)
                        DO UPDATE SET frequency = EXCLUDED.frequency
                        """,
                        (colour.title(), frequency),
                    )

        connection.close()
        print(
            "\n6. PostgreSQL: colour frequencies saved successfully "
            "to bincom_colour_frequencies."
        )

    except ImportError:
        print(
            "\n6. PostgreSQL: install the driver first with "
            'pip install "psycopg[binary]".'
        )
    except Exception as error:
        print(f"\n6. PostgreSQL: database operation failed: {error}")


def recursive_search(numbers, target, index=0):
    """Return the index of target using recursion, or -1 if not found."""
    if index >= len(numbers):
        return -1
    if numbers[index] == target:
        return index
    return recursive_search(numbers, target, index + 1)


def run_recursive_search():
    print("\n7. BONUS - RECURSIVE SEARCH")
    numbers = [4, 8, 15, 16, 23, 42, 50, 64]

    try:
        target = int(input(f"Enter a number to search in {numbers}: "))
        result = recursive_search(numbers, target)

        if result == -1:
            print(f"{target} was not found in the list.")
        else:
            print(f"{target} was found at index {result}.")
    except ValueError:
        print("Please enter a valid whole number.")


def generate_binary_and_convert():
    """Generate a four-bit binary string and convert it to base 10."""
    binary_number = "".join(random.choice("01") for _ in range(4))
    decimal_number = int(binary_number, 2)

    print("\n8. RANDOM BINARY NUMBER CONVERSION")
    print(f"Generated binary number: {binary_number}")
    print(f"Base-10 (decimal) equivalent: {decimal_number}")


def fibonacci_sum(number_of_terms=50):
    """Return the first number_of_terms Fibonacci values and their sum."""
    sequence = []
    first, second = 0, 1

    for _ in range(number_of_terms):
        sequence.append(first)
        first, second = second, first + second

    return sequence, sum(sequence)


def run_fibonacci():
    sequence, total = fibonacci_sum(50)

    print("\n9. SUM OF THE FIRST 50 FIBONACCI NUMBERS")
    print(f"Sequence: {sequence}")
    print(f"Sum: {total}")


def main():
    print("BINCOM ICT SOLUTIONS - PYTHON BASIC DEVELOPER TEST")

    try:
        colours = extract_colours(HTML_FILE)
        frequencies = analyse_colours(colours)
        save_frequencies_to_postgresql(frequencies)
    except (FileNotFoundError, ValueError) as error:
        print(f"\nData analysis error: {error}")

    run_recursive_search()
    generate_binary_and_convert()
    run_fibonacci()


if __name__ == "__main__":
    main()
