import subprocess
import sys


def test_verbose_flag_toggles_logging(tmp_path):
    sample = tmp_path / "file.txt"
    sample.write_text("content")
    out = tmp_path / "out.html"

    result = subprocess.run(
        [sys.executable, "documenter.py", str(tmp_path), "-o", str(out)],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Processing file" not in result.stderr

    result_verbose = subprocess.run(
        [sys.executable, "documenter.py", str(tmp_path), "-o", str(out), "--verbose"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert "Processing file" in result_verbose.stderr
