# Documenter.py — A Python Script for Generating HTML Documentation

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Overview

`documenter.py` is a Python script that automatically generates an HTML-based documentation of your project’s file structure and contents. It walks through a specified project directory, lists all subdirectories and files, and includes the code or text from each file in an easy-to-navigate HTML page.

Notable features include:

- **Copy Button** next to each file for quick copy-pasting of individual file contents.
- **Copy ALL Text** button to copy every file’s content into your clipboard at once.
- **Optional Sensitive Information Masking** (removes `$host`, `$user`, `$pass`, `$db`, `$charset` lines).
- **Ignore Mechanism** to skip certain directories/files (like `.git`, `.DS_Store`, etc.).
- **No External Dependencies** beyond Python’s standard library.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Arguments](#command-line-arguments)
- [Example](#example)
- [License](#license)
- [Author](#author)

## Installation

1. **Clone the repository** (or download the script directly):
   ```bash
   git clone https://github.com/josephbartlett/code-documenter.git
   ```
2. **Navigate into the directory**:
   ```bash
   cd code-documenter
   ```
3. Ensure you have **Python 3.x** installed.  
4. No additional dependencies are required.

## Usage

Run the script with Python, specifying the target directory you want documented:

```bash
python documenter.py /path/to/project
```

### Command-Line Arguments

- **`directory`** *(required)*  
  Path to the project directory you want to document.

- **`-o`, `--output`** *(optional)*  
  Name of the output HTML file.  
  *Default:* `<directoryname>_Documentation.html`.

- **`-r`, `--remove_sensitive`** *(optional)*  
  Remove sensitive information (lines containing `$host`, `$user`, `$pass`, `$db`, `$charset`).  

- **`-i`, `--ignore_list`** *(optional)*  
  Provide a list of substrings or filenames to ignore.  
  Example: `-i node_modules venv test.log`

- **`--include_all`** *(optional)*  
  Override all ignores and include every file/folder in the documentation.

## Example

```bash
# Generate documentation for the "my_project" folder
python documenter.py my_project

# Generate documentation and output to custom filename
python documenter.py my_project -o docs.html

# Generate documentation, remove sensitive info, and ignore "node_modules"
python documenter.py my_project -r -i node_modules

# Ignore nothing (include all files)
python documenter.py my_project --include_all
```

When complete, you’ll have an HTML file containing:

1. A clickable list of your project’s folders and files.
2. File content in `<pre>` blocks for each file, with “Copy” buttons.
3. A “Copy ALL Text” button that copies content from all files.

## License

This project is licensed under the [MIT License](LICENSE).

## Author

**Joseph Bartlett**  
Email: [jbartlett.gh@pm.me](mailto:jbartlett.gh@pm.me)  
GitHub: [github.com/josephbartlett](https://github.com/josephbartlett)

Feel free to reach out or open an issue if you have any questions or suggestions.