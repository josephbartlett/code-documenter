import os
import html
import argparse

def is_text_file(filepath):
    """Check if a file is a text file by attempting to read it as UTF-8."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            file.read()
        return True
    except:
        print(f"Skipping non-text file: {filepath}")
        return False

def remove_sensitive_info(content):
    """Mask certain sensitive lines in the file."""
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "$host =" in line or "$db =" in line or "$user =" in line or "$pass =" in line or "$charset =" in line:
            parts = line.split('=')
            if len(parts) > 1:
                lines[i] = parts[0] + "= '******';"
    return '\n'.join(lines)

def should_ignore(path, ignore_list, include_all):
    """
    Decide whether to ignore a file or directory, based on:
    - The default ignore list (if include_all is False).
    - The user-provided ignore list.
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
    """
    Walk through the directory, build an HTML file that includes:
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

        for subdir, dirs, files in os.walk(root_dir):
            # Check if subdir is ignored
            if should_ignore(os.path.relpath(subdir, root_dir), ignore_list, include_all):
                # Modify 'dirs' in place to skip subdirectories inside ignored folder
                dirs[:] = []
                continue

            dir_path = os.path.relpath(subdir, root_dir)
            if dir_path == ".":
                # top-level directory
                dir_path_display = os.path.basename(root_dir) or root_dir
            else:
                dir_path_display = dir_path

            # Print this directory
            output.write(f"<li>{html.escape(dir_path_display)}\n<ul>\n")

            for file in files:
                # Check if file is ignored
                rel_path = os.path.relpath(os.path.join(subdir, file), root_dir)
                if should_ignore(rel_path, ignore_list, include_all):
                    continue

                anchor_name = html.escape(rel_path.replace("\\", "/").replace(" ", "_"))
                output.write(f"<li><a href='#{anchor_name}'>{html.escape(rel_path)}</a></li>\n")

            output.write("</ul></li>\n")

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

                print(f"Processing file: {relative_path}")
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
                        print(f"Error reading file {filepath}: {e}")
                        output.write("<p><em>Error reading file.</em></p>\n")
                else:
                    output.write("<p><em>Binary file or non-readable content</em></p>\n")

        output.write("</body></html>\n")

def parse_arguments():
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
        default=None,
        help="List of folder/file substrings to ignore (e.g. .git .DS_Store)"
    )
    parser.add_argument(
        "--include_all",
        action="store_true",
        help="Include all files (override all ignores, including default ignores)."
    )

    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_arguments()
    root_directory = args.directory.rstrip("\\/")

    # Default ignores - add or remove as you see fit
    default_ignores = [".git", ".gitignore", ".DS_Store"]

    # Merge user-supplied ignores with defaults (if not include_all)
    if args.ignore_list:
        merged_ignores = default_ignores + args.ignore_list
    else:
        merged_ignores = default_ignores

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