#!/usr/bin/env python3
import glob
import os


def remove_trailing_whitespace(file_path):
    """Remove trailing whitespace from a file."""
    with open(file_path) as f:
        lines = f.readlines()

    # Remove trailing whitespace from each line
    cleaned_lines = [line.rstrip() + "\n" for line in lines]

    # Remove any trailing newlines at the end of the file
    while cleaned_lines and cleaned_lines[-1] == "\n":
        cleaned_lines.pop()
    if cleaned_lines:
        cleaned_lines.append("\n")

    with open(file_path, "w") as f:
        f.writelines(cleaned_lines)


def main():
    # Get all Python files recursively
    python_files = []
    for root, _, _ in os.walk("."):
        if "venv" in root or ".git" in root:
            continue
        python_files.extend(glob.glob(os.path.join(root, "*.py")))

    # Process each file
    for file_path in python_files:
        print(f"Processing {file_path}")
        remove_trailing_whitespace(file_path)


if __name__ == "__main__":
    main()
