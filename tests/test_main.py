"""Unit tests for main module."""

from pathlib import Path

import pytest
import typer

from main import (
    FileType,
    detect_file_type,
    find_pdf_files,
    find_png_files,
    process_single_file,
)


class TestFindPngFiles:
    """Tests for find_png_files function."""

    def test_empty_directory(self, tmp_path: Path) -> None:
        """Returns empty list when directory has no PNG files."""
        result = find_png_files(tmp_path)
        assert result == []

    def test_finds_png_files(self, tmp_path: Path) -> None:
        """Returns list of PNG files in natural sort order."""
        (tmp_path / "image1.png").touch()
        (tmp_path / "image2.png").touch()
        (tmp_path / "image10.png").touch()

        result = find_png_files(tmp_path)

        assert len(result) == 3
        assert result[0].name == "image1.png"
        assert result[1].name == "image2.png"
        assert result[2].name == "image10.png"

    def test_case_insensitive(self, tmp_path: Path) -> None:
        """Finds both .png and .PNG files."""
        (tmp_path / "lower.png").touch()
        (tmp_path / "upper.PNG").touch()

        result = find_png_files(tmp_path)

        assert len(result) == 2

    def test_ignores_other_files(self, tmp_path: Path) -> None:
        """Does not include non-PNG files."""
        (tmp_path / "image.png").touch()
        (tmp_path / "document.pdf").touch()
        (tmp_path / "readme.txt").touch()

        result = find_png_files(tmp_path)

        assert len(result) == 1
        assert result[0].name == "image.png"


class TestFindPdfFiles:
    """Tests for find_pdf_files function."""

    def test_empty_directory(self, tmp_path: Path) -> None:
        """Returns empty list when directory has no PDF files."""
        result = find_pdf_files(tmp_path)
        assert result == []

    def test_finds_pdf_files(self, tmp_path: Path) -> None:
        """Returns list of PDF files in natural sort order."""
        (tmp_path / "doc1.pdf").touch()
        (tmp_path / "doc2.pdf").touch()
        (tmp_path / "doc10.pdf").touch()

        result = find_pdf_files(tmp_path)

        assert len(result) == 3
        assert result[0].name == "doc1.pdf"
        assert result[1].name == "doc2.pdf"
        assert result[2].name == "doc10.pdf"

    def test_case_insensitive(self, tmp_path: Path) -> None:
        """Finds both .pdf and .PDF files."""
        (tmp_path / "lower.pdf").touch()
        (tmp_path / "upper.PDF").touch()

        result = find_pdf_files(tmp_path)

        assert len(result) == 2

    def test_ignores_other_files(self, tmp_path: Path) -> None:
        """Does not include non-PDF files."""
        (tmp_path / "document.pdf").touch()
        (tmp_path / "image.png").touch()
        (tmp_path / "readme.txt").touch()

        result = find_pdf_files(tmp_path)

        assert len(result) == 1
        assert result[0].name == "document.pdf"


class TestDetectFileType:
    """Tests for detect_file_type function."""

    def test_png_only(self, tmp_path: Path) -> None:
        """Returns PNG when only PNG files present."""
        (tmp_path / "image.png").touch()

        result = detect_file_type(tmp_path)

        assert result == FileType.PNG

    def test_pdf_only(self, tmp_path: Path) -> None:
        """Returns PDF when only PDF files present."""
        (tmp_path / "document.pdf").touch()

        result = detect_file_type(tmp_path)

        assert result == FileType.PDF

    def test_empty_directory_raises(self, tmp_path: Path) -> None:
        """Raises Exit when no PNG or PDF files found."""
        with pytest.raises(typer.Exit) as exc_info:
            detect_file_type(tmp_path)

        assert exc_info.value.exit_code == 1

    def test_mixed_files_raises(self, tmp_path: Path) -> None:
        """Raises Exit when both PNG and PDF files present."""
        (tmp_path / "image.png").touch()
        (tmp_path / "document.pdf").touch()

        with pytest.raises(typer.Exit) as exc_info:
            detect_file_type(tmp_path)

        assert exc_info.value.exit_code == 1


class TestProcessSingleFile:
    """Tests for process_single_file function."""

    def test_png_file(self, tmp_path: Path) -> None:
        """Returns PNG type and file list for PNG file."""
        png_file = tmp_path / "image.png"
        png_file.touch()

        file_type, files = process_single_file(png_file)

        assert file_type == FileType.PNG
        assert files == [png_file]

    def test_pdf_file(self, tmp_path: Path) -> None:
        """Returns PDF type and file list for PDF file."""
        pdf_file = tmp_path / "document.pdf"
        pdf_file.touch()

        file_type, files = process_single_file(pdf_file)

        assert file_type == FileType.PDF
        assert files == [pdf_file]

    def test_unsupported_extension_raises(self, tmp_path: Path) -> None:
        """Raises Exit for unsupported file extensions."""
        txt_file = tmp_path / "readme.txt"
        txt_file.touch()

        with pytest.raises(typer.Exit) as exc_info:
            process_single_file(txt_file)

        assert exc_info.value.exit_code == 1
