#!/usr/bin/env python3
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if __package__:
    from main.utils.book_converter import BookConverter
else:
    # Keep direct script execution working without mutating ``sys.path``.
    from utils.book_converter import BookConverter


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Convert books in Knowledge_base/Books to Markdown format using MarkItDown."
        )
    )
    parser.add_argument(
        "--books-dir",
        type=Path,
        default=PROJECT_ROOT / "Knowledge_base" / "Books",
        help="Path to the books directory (default: Knowledge_base/Books)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Path to output markdown files (default: same directory as books)",
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=[".epub", ".pdf", ".docx"],
        help="Allowed file extensions (default: .epub .pdf .docx)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing markdown files",
    )
    parser.add_argument(
        "--delete-original",
        action="store_true",
        default=True,
        help=(
            "Delete original book files (.epub, .pdf, etc.) after successful "
            "conversion (default: True)"
        ),
    )
    parser.add_argument(
        "--keep-original",
        action="store_false",
        dest="delete_original",
        help="Keep original book files after conversion",
    )

    args = parser.parse_args()

    print("==========================================")
    print("      Book Conversion via MarkItDown     ")
    print("==========================================")
    print(f"Books Directory:  {args.books_dir.resolve()}")
    output_dir = args.output_dir.resolve() if args.output_dir else "Same as books"
    print(f"Output Directory: {output_dir}")
    print(f"Extensions:       {', '.join(args.extensions)}")
    print(f"Overwrite:        {args.force}")
    print(f"Delete Original:  {args.delete_original}")
    print("------------------------------------------\n")

    converter = BookConverter(output_dir=args.output_dir)
    converted = converter.convert_directory(
        input_dir=args.books_dir,
        extensions=args.extensions,
        force=args.force,
        delete_original=args.delete_original,
    )

    print("\n------------------------------------------")
    print(f"Processing complete! Converted/verified {len(converted)} book(s).")
    print("==========================================")


if __name__ == "__main__":
    main()
