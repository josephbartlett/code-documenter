import os
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from documenter import write_directory_contents_to_html, DEFAULT_IGNORES, remove_sensitive_info


def _find_child(li_elem, name):
    ul = li_elem.find('ul')
    if ul is None:
        return None
    for child in ul.findall('li'):
        text = (child.text or '').strip()
        if text == name:
            return child
    return None


def test_nested_directory_structure(tmp_path):
    root = tmp_path / "root"
    (root / "a" / "b").mkdir(parents=True)
    (root / "a" / "b" / "file.txt").write_text("hi")

    output_file = tmp_path / "out.html"
    write_directory_contents_to_html(str(root), str(output_file), False, DEFAULT_IGNORES, False)

    html = output_file.read_text()
    start = html.index("<h2>Project Structure</h2>")
    start = html.index("</h2>", start) + len("</h2>")
    end = html.index("<h2>Project Contents</h2>")
    structure = html[start:end]
    tree = ET.fromstring(f"<root>{structure}</root>")

    top_ul = tree.find('ul')
    root_li = top_ul.find('li')

    dir_a = _find_child(root_li, 'a')
    assert dir_a is not None

    dir_ab = _find_child(dir_a, 'a/b')
    assert dir_ab is not None


def test_remove_sensitive_info_varied_formats():
    content = (
        "$host = 'localhost';\n"
        "$db='mydb'\n"
        "$user =    'admin' ;\n"
        "$pass=secret;\n"
        "$charset=\"utf8\"\n"
        "normal line\n"
    )
    expected = (
        "$host = '******';\n"
        "$db='******'\n"
        "$user =    '******' ;\n"
        "$pass=******;\n"
        "$charset=\"******\"\n"
        "normal line\n"
    )
    assert remove_sensitive_info(content) == expected
