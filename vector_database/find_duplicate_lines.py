from collections import defaultdict
import sys

def find_duplicates_with_positions(path):
    # Map each line to the list of its line numbers
    positions = defaultdict(list)
    with open(path, 'r', encoding='utf-8') as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.rstrip('\n')
            positions[line].append(lineno)

    # Keep only those lines that appear more than once
    return {line: nums for line, nums in positions.items() if len(nums) > 1}

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <text_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    duplicates = find_duplicates_with_positions(file_path)

    if not duplicates:
        print("No duplicate lines found.")
    else:
        print("Duplicate lines:")
        for line, nums in duplicates.items():
            count = len(nums)
            print(f"  {repr(line)} → {count} times on lines {nums}")
