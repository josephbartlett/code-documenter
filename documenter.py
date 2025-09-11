"""Generate a single-page HTML overview of a project directory.

The script walks a directory tree and produces an HTML document
containing the structure and contents of each readable file, complete
with copy-to-clipboard helpers. Sensitive database connection values
can be masked and certain paths ignored. Key helpers include
``write_directory_contents_to_html`` for building the page,
``remove_sensitive_info`` for obfuscation, and ``is_text_file`` for
detecting binary files.

Command line usage:

``python documenter.py <directory> [-o OUTPUT] [-r] [-i IGNORE ...] [--include_all] [-v]``
"""

import os
import html
import argparse
import re
import logging

DEFAULT_IGNORES = [".git", ".gitignore", ".DS_Store"]

def is_text_file(filepath):
    """Check if the file appears to contain UTF-8 text.

    Parameters:
        filepath (str): Path to the file to inspect.

    Returns:
        bool: True when the file decodes as UTF-8 text, False otherwise.
    """
    try:
        with open(filepath, "rb") as file:
            chunk = file.read(1024)
        if b"\x00" in chunk:
            logging.info("Skipping non-text file: %s", filepath)
            return False
        chunk.decode("utf-8")
        return True
    except (UnicodeDecodeError, OSError):
        logging.info("Skipping non-text file: %s", filepath)
        return False

def remove_sensitive_info(content):
    """Mask database connection values while preserving formatting.

    Parameters:
        content (str): Original file contents to scrub.

    Returns:
        str: Content with connection values replaced by asterisks.
    """
    pattern = re.compile(r"(\$(?:host|db|user|pass|charset)\s*=\s*)([^\r\n]*)(\r?\n?)", re.IGNORECASE)

    def mask_line(line):
        match = pattern.search(line)
        if not match:
            return line

        prefix = match.group(1)
        rest = match.group(2)
        newline = match.group(3)

        leading_ws_match = re.match(r"\s*", rest)
        leading_ws = leading_ws_match.group(0)
        rest = rest[len(leading_ws):]

        if rest.startswith("'") or rest.startswith('"'):
            quote = rest[0]
            closing_index = rest.find(quote, 1)
            if closing_index == -1:
                closing = ''
                trailing = rest[1:]
            else:
                closing = quote
                trailing = rest[closing_index + 1:]
        else:
            quote = ''
            closing = ''
            value_match = re.match(r"[^\s;]*", rest)
            trailing = rest[value_match.end():]

        return f"{prefix}{leading_ws}{quote}******{closing}{trailing}{newline}"

    lines = content.splitlines(True)
    return ''.join(mask_line(line) for line in lines)

def should_ignore(path, ignore_list, include_all):
    """Determine whether a path should be skipped.

    Parameters:
        path (str): Relative path of the file or directory.
        ignore_list (list[str]): Collection of substrings that trigger ignoring.
        include_all (bool): If True, ignore rules are bypassed.

    Returns:
        bool: True when the path should be ignored.
    """
    # If user has specified --include_all, do not ignore anything.
    if include_all:
        return False
    
    # Check if the path (folder or file) matches an entry in ignore_list
    for ignore_term in ignore_list:
        if ignore_term in path:
            return True
    return False

def write_directory_contents_to_html(root_dir, output_file, remove_sensitive, ignore_list, include_all):
    """Create an HTML file describing the directory's structure and files.

    Parameters:
        root_dir (str): Directory to document.
        output_file (str): Path of the HTML file to write.
        remove_sensitive (bool): If True, mask sensitive information.
        ignore_list (list[str]): Substrings identifying files or folders to skip.
        include_all (bool): Whether to override ignoring behavior.

    Returns:
        None

    Walk through the directory and build an HTML file that includes:
        - Directory structure
        - File contents (with an option to mask sensitive information)
        - Copy buttons for individual files
        - A button for copying all text
    """
    with open(output_file, 'w', encoding='utf-8') as output:
        # --- HTML HEAD WITH JAVASCRIPT FOR COPY FUNCTIONALITY ---
        output.write("""<html>
<head>
    <title>Project Documentation</title>
    <style>
        body {
            font-family: Arial, sans-serif;
        }
        pre {
            background-color: #f9f9f9;
            padding: 1em;
            border: 1px solid #ccc;
            white-space: pre-wrap;       /* Since some code might be long lines */
            word-wrap: break-word;       /* Wrap long lines */
        }
        .copy-button {
            margin-left: 10px;
            padding: 3px 8px;
            font-size: 0.8em;
            cursor: pointer;
        }
    </style>
    <script>
        // Generic function to copy text to clipboard
        function copyText(text) {
            navigator.clipboard.writeText(text)
                .then(function() {
                    alert("Copied to clipboard!");
                })
                .catch(function(err) {
                    console.error("Error copying text: ", err);
                });
        }

        // Copies the text content of a specific <pre> block
        function copyFileContent(elementId) {
            var text = document.getElementById(elementId).innerText;
            copyText(text);
        }

        // Copies ALL text from all <pre> blocks
        function copyAllText() {
            var allText = "";
            var codeBlocks = document.getElementsByTagName("pre");
            for (var i = 0; i < codeBlocks.length; i++) {
                allText += codeBlocks[i].innerText + "\\n";
            }
            copyText(allText);
        }
    </script>
</head>
<body>
""")

        # --- BUTTON FOR COPYING ALL TEXT ---
        output.write("<h1>Project Documentation</h1>\n")
        output.write("<button class='copy-button' onclick='copyAllText()'>Copy ALL Text</button>\n")

        # --- DIRECTORY STRUCTURE ---
        output.write("<h2>Project Structure</h2>\n")
        output.write("<ul>\n")

        def write_structure(current_dir):
            """Recursively write the directory tree as nested lists.

            Parameters:
                current_dir (str): Directory currently being processed.

            Returns:
                None
            """
            rel_dir = os.path.relpath(current_dir, root_dir)
            if should_ignore(rel_dir, ignore_list, include_all):
                return

            if rel_dir == ".":
                display_name = os.path.basename(root_dir) or root_dir
            else:
                display_name = rel_dir

            output.write(f"<li>{html.escape(display_name)}\n<ul>\n")

            entries = sorted(os.listdir(current_dir))
            dirs = [e for e in entries if os.path.isdir(os.path.join(current_dir, e))]
            files = [e for e in entries if os.path.isfile(os.path.join(current_dir, e))]

            for d in dirs:
                sub_path = os.path.join(current_dir, d)
                write_structure(sub_path)

            for f in files:
                rel_path = os.path.relpath(os.path.join(current_dir, f), root_dir)
                if should_ignore(rel_path, ignore_list, include_all):
                    continue
                anchor_name = html.escape(rel_path.replace("\\", "/").replace(" ", "_"))
                output.write(f"<li><a href='#{anchor_name}'>{html.escape(rel_path)}</a></li>\n")

            output.write("</ul>\n</li>\n")

        write_structure(root_dir)

        output.write("</ul>\n")

        # --- FILE CONTENTS ---
        output.write("<h2>Project Contents</h2>\n")

        for subdir, dirs, files in os.walk(root_dir):
            # Skip processing contents for an ignored directory
            if should_ignore(os.path.relpath(subdir, root_dir), ignore_list, include_all):
                dirs[:] = []
                continue

            for file in files:
                filepath = os.path.join(subdir, file)
                relative_path = os.path.relpath(filepath, root_dir)

                # Skip ignored file
                if should_ignore(relative_path, ignore_list, include_all):
                    continue

                anchor_name = html.escape(relative_path.replace("\\", "/").replace(" ", "_"))

                logging.info("Processing file: %s", relative_path)
                output.write(f"<h3 id='{anchor_name}'>{html.escape(relative_path)}")

                # Add the copy-button near each filename
                output.write(f" <button class='copy-button' onclick=\"copyFileContent('{anchor_name}_pre')\">Copy</button>")
                output.write("</h3>\n")

                if is_text_file(filepath):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if remove_sensitive:
                                content = remove_sensitive_info(content)
                            content_escaped = html.escape(content)
                            # Use a <pre> block with an id for each file's content
                            output.write(f"<pre id='{anchor_name}_pre'>{content_escaped}</pre>\n")
                    except Exception as e:
                        logging.warning("Error reading file %s: %s", filepath, e)
                        output.write("<p><em>Error reading file.</em></p>\n")
                else:
                    output.write("<p><em>Binary file or non-readable content</em></p>\n")

        output.write("</body></html>\n")

def parse_arguments():
    """Parse command line options for the script.

    Returns:
        argparse.Namespace: Parsed command line arguments.
    """
    parser = argparse.ArgumentParser(
        description="Generate HTML documentation for a project directory, with options to mask sensitive info."
    )
    parser.add_argument("directory", help="Path to the project directory")
    parser.add_argument("-o", "--output", help="Output HTML file name", default=None)
    parser.add_argument(
        "-r",
        "--remove_sensitive",
        help="Remove sensitive information from files",
        action="store_true"
    )
    parser.add_argument(
        "-i",
        "--ignore_list",
        nargs="*",
        default=[],
        help="List of folder/file substrings to ignore (e.g. .git .DS_Store)"
    )
    parser.add_argument(
        "--include_all",
        action="store_true",
        help="Include all files (override all ignores, including default ignores)."
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose (INFO) logging",
    )
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_arguments()
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING)
    root_directory = args.directory.rstrip("\\/")

    # Merge user-supplied ignores with defaults
    merged_ignores = DEFAULT_IGNORES + args.ignore_list

    if args.output:
        output_filename = args.output
    else:
        directory_name = os.path.basename(root_directory)
        output_filename = directory_name + "_Documentation.html" if directory_name else "Project_Documentation.html"

    write_directory_contents_to_html(
        root_directory,
        output_filename,
        args.remove_sensitive,
        merged_ignores,
        args.include_all
    )
