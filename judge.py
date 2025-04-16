import os
import shutil
import subprocess
from pathlib import Path
from difflib import unified_diff


base_dir = Path(__file__).parent
testcases_dir = base_dir / "testcases"
input_file = base_dir / "input.txt"


output_files = ["tokens.txt", "lexical_errors.txt", "symbol_table.txt"]


def read_file_lines(path):
    with open(path, encoding='utf-8') as f:
        return [line.rstrip() for line in f.readlines()]

def clean_symbol_table(lines):
    return sorted(line.split('\t', 1)[1] if '\t' in line else line for line in lines)


def compare_files(file1, file2, is_symbol_table=False):
    lines1 = read_file_lines(file1)
    lines2 = read_file_lines(file2)

    if is_symbol_table:
        lines1 = clean_symbol_table(lines1)
        lines2 = clean_symbol_table(lines2)

    diff = list(unified_diff(lines1, lines2, fromfile='expected', tofile='actual', lineterm=''))
    return diff


for test_dir in sorted(testcases_dir.glob("T*")):
    print(f"\nRunning test: {test_dir.name}")

    
    shutil.copy(test_dir / "input.txt", input_file)


    result = subprocess.run(["python", "compiler.py"], cwd=base_dir)


    for fname in output_files:
        expected = test_dir / fname
        actual = base_dir / fname
        is_symbol = fname == "symbol_table.txt"

        diff = compare_files(expected, actual, is_symbol_table=is_symbol)

        if not diff:
            print(f"  ✅ {fname}: No differences")
        else:
            print(f"  ❌ {fname}: Differences found")
            print('\n'.join(diff[:10]))
