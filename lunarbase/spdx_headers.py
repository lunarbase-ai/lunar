import os

def check_and_add_header(filepath, header_text, presence_check_string):
    """
    Checks if a file contains a specific string (presence_check_string).
    If the string is NOT found, it prepends the header_text to the file.

    Args:
        filepath (str): The path to the file.
        header_text (str): The header text to add if presence_check_string is not found.
        presence_check_string (str): The string to search for within the file's content.
                                     If found, the header_text is not added.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if presence_check_string in content:
            print(f"'{presence_check_string}' found. Header not added to: {filepath}")
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(header_text + content)
            print(f"Header added to: {filepath}")
    except Exception as e:
        print(f"Error processing file {filepath}: {e}")

def main():
    target_directory = '/home/pedro/lunar/lunarbase'
    header_to_add = """#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
"""
    # This string will be checked for presence. If it exists, the header won't be added.
    string_to_check_for_presence = "SPDX-FileCopyrightText"

    for root, _, files in os.walk(target_directory):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                check_and_add_header(filepath, header_to_add, string_to_check_for_presence)

if __name__ == "__main__":
    main()