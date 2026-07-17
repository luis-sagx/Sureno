from __future__ import annotations

from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "coverage.xml"
SOURCE_DIRS = ("models", "routes")
ROOT_FILES = ("app.py", "config.py")


def iter_python_files() -> list[Path]:
    files: list[Path] = []

    for relative in ROOT_FILES:
        path = ROOT / relative
        if path.exists():
            files.append(path)

    for source_dir in SOURCE_DIRS:
        base_dir = ROOT / source_dir
        if not base_dir.exists():
            continue
        for path in sorted(base_dir.rglob("*.py")):
            if "__pycache__" not in path.parts:
                files.append(path)

    return files


def executable_lines(path: Path) -> list[int]:
    lines: list[int] = []
    for number, content in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = content.strip()
        if stripped and not stripped.startswith("#"):
            lines.append(number)
    return lines


def main() -> None:
    files = iter_python_files()
    total_lines = 0

    coverage = Element(
        "coverage",
        {
            "version": "1.0",
            "timestamp": "0",
            "lines-valid": "0",
            "lines-covered": "0",
            "line-rate": "0",
            "branches-valid": "0",
            "branches-covered": "0",
            "branch-rate": "0",
            "complexity": "0",
        },
    )

    sources = SubElement(coverage, "sources")
    SubElement(sources, "source").text = str(ROOT)

    packages = SubElement(coverage, "packages")
    package = SubElement(
        packages,
        "package",
        {"name": ".", "line-rate": "0", "branch-rate": "0", "complexity": "0"},
    )
    classes = SubElement(package, "classes")

    for path in files:
        relative_path = path.relative_to(ROOT).as_posix()
        class_name = relative_path.removesuffix(".py").replace("/", ".")
        class_element = SubElement(
            classes,
            "class",
            {
                "name": class_name,
                "filename": relative_path,
                "line-rate": "0",
                "branch-rate": "0",
                "complexity": "0",
            },
        )
        lines_element = SubElement(class_element, "lines")
        for line_number in executable_lines(path):
            total_lines += 1
            SubElement(lines_element, "line", {"number": str(line_number), "hits": "0"})

    coverage.set("lines-valid", str(total_lines))
    tree = ElementTree(coverage)
    tree.write(OUTPUT, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    main()
