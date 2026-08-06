import os
from pathlib import Path
from typing import Optional, List
from markitdown import MarkItDown


class BookConverter:
    """Utility class to convert books (EPUB, PDF, etc.) into Markdown format using MarkItDown."""

    def __init__(self, output_dir: Optional[Path] = None):
        self.md = MarkItDown()
        self.output_dir = output_dir

    def convert_file(self, file_path: Path, force: bool = False, delete_original: bool = False) -> Path:
        """Converts a single book file to Markdown.

        Args:
            file_path: Path to the input book file.
            force: If True, overwrites existing markdown output.
            delete_original: If True, deletes the source book file after successful conversion.

        Returns:
            Path to the generated markdown file.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

        destination_dir = self.output_dir if self.output_dir else file_path.parent
        destination_dir.mkdir(parents=True, exist_ok=True)

        output_file = destination_dir / f"{file_path.stem}.md"

        if output_file.exists() and not force:
            print(f"[SKIP] {output_file.name} already exists. Use force=True to overwrite.")
            if delete_original and file_path.exists():
                file_path.unlink()
                print(f"[DELETED] Removed original file: {file_path.name}")
            return output_file

        print(f"[CONVERTING] {file_path.name} -> {output_file.name} ...")
        result = self.md.convert(str(file_path))

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result.text_content)

        print(f"[SUCCESS] Saved to {output_file}")

        if delete_original and file_path.exists():
            file_path.unlink()
            print(f"[DELETED] Removed original file: {file_path.name}")

        return output_file

    def convert_directory(
        self,
        input_dir: Path,
        extensions: Optional[List[str]] = None,
        force: bool = False,
        delete_original: bool = False
    ) -> List[Path]:
        """Converts all matching book files in a directory.

        Args:
            input_dir: Path to the directory containing books.
            extensions: List of extensions to convert (default: ['.epub', '.pdf', '.docx']).
            force: If True, overwrites existing markdown outputs.
            delete_original: If True, deletes source book files after successful conversion.

        Returns:
            List of paths to converted markdown files.
        """
        input_dir = Path(input_dir)
        if not input_dir.exists() or not input_dir.is_dir():
            raise ValueError(f"Input directory does not exist or is not a directory: {input_dir}")

        if extensions is None:
            extensions = [".epub", ".pdf", ".docx"]

        # Standardize extensions to lowercase with leading dot
        ext_set = {ext if ext.startswith(".") else f".{ext}" for ext in extensions}
        ext_set = {ext.lower() for ext in ext_set}

        converted_files = []
        book_files = [
            f for f in input_dir.iterdir()
            if f.is_file() and f.suffix.lower() in ext_set
        ]

        if not book_files:
            print(f"No matching book files found in {input_dir}")
            return []

        print(f"Found {len(book_files)} book(s) to process in {input_dir}:")
        for book_file in sorted(book_files):
            try:
                out_path = self.convert_file(book_file, force=force, delete_original=delete_original)
                converted_files.append(out_path)
            except Exception as e:
                print(f"[ERROR] Failed to convert {book_file.name}: {e}")

        return converted_files
