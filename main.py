"""CLI tool to convert PNG/PDF files to PowerPoint presentations."""

import shutil
import tempfile
from enum import Enum
from pathlib import Path

import typer
from natsort import natsorted
from pdf2image import convert_from_path
from pptx import Presentation
from pptx.util import Inches
from tqdm import tqdm

app = typer.Typer(help="Convert PNG/PDF files to PowerPoint presentation")


class FileType(Enum):
    """Supported input file types."""

    PNG = "png"
    PDF = "pdf"


def find_png_files(folder: Path) -> list[Path]:
    """Find all PNG files in the given folder.

    Args:
        folder: Path to the folder to search for PNG files.

    Returns:
        List of Path objects for PNG files, sorted in natural order.
    """
    png_files: list[Path] = []
    for ext in ["*.png", "*.PNG"]:
        png_files.extend(folder.glob(ext))
    return natsorted(png_files)


def find_pdf_files(folder: Path) -> list[Path]:
    """Find all PDF files in the given folder.

    Args:
        folder: Path to the folder to search for PDF files.

    Returns:
        List of Path objects for PDF files, sorted in natural order.
    """
    pdf_files: list[Path] = []
    for ext in ["*.pdf", "*.PDF"]:
        pdf_files.extend(folder.glob(ext))
    return natsorted(pdf_files)


def detect_file_type(folder: Path) -> FileType:
    """Detect whether folder contains PNG or PDF files.

    Args:
        folder: Path to the folder to check.

    Returns:
        FileType enum indicating the detected file type.

    Raises:
        typer.Exit: If no files found, or mixed file types detected.
    """
    png_files = find_png_files(folder)
    pdf_files = find_pdf_files(folder)

    has_png = len(png_files) > 0
    has_pdf = len(pdf_files) > 0

    if not has_png and not has_pdf:
        typer.echo(f"Error: No PNG or PDF files found in {folder}", err=True)
        raise typer.Exit(code=1)

    if has_png and has_pdf:
        typer.echo(
            f"Error: Mixed PNG and PDF files detected in {folder}. "
            "Please use separate folders.",
            err=True,
        )
        raise typer.Exit(code=1)

    if has_png:
        return FileType.PNG
    return FileType.PDF


def process_single_file(file_path: Path) -> tuple[FileType, list[Path]]:
    """Process a single PNG or PDF file.

    Args:
        file_path: Path to the single file to process.

    Returns:
        Tuple of (FileType, list of file paths to process).
        For PNG: returns PNG file type and single-item list.
        For PDF: returns PDF file type and single-item list.

    Raises:
        typer.Exit: If file type is not supported.
    """
    suffix = file_path.suffix.lower()

    match suffix:
        case ".png":
            return FileType.PNG, [file_path]
        case ".pdf":
            return FileType.PDF, [file_path]
        case _:
            typer.echo(
                f"Error: Unsupported file type '{suffix}'. "
                "Only .png and .pdf files are supported.",
                err=True,
            )
            raise typer.Exit(code=1)


def convert_pdf_to_pngs(pdf_files: list[Path], dpi: int, temp_dir: Path) -> list[Path]:
    """Convert PDF files to PNG images.

    Args:
        pdf_files: List of PDF file paths to convert.
        dpi: DPI resolution for conversion (higher = better quality).
        temp_dir: Directory to store temporary PNG files.

    Returns:
        List of Path objects for generated PNG files in natural order.

    Raises:
        typer.Exit: If PDF conversion fails.
    """
    png_paths = []

    # Progress bar for PDF files
    with tqdm(pdf_files, desc="Converting PDFs", unit="file") as pbar:
        for pdf_file in pbar:
            try:
                pbar.set_postfix_str(f"Processing: {pdf_file.name}")

                # Convert PDF to images
                images = convert_from_path(str(pdf_file), dpi=dpi)

                if not images:
                    tqdm.write(f"Error: No pages found in {pdf_file.name}")
                    raise typer.Exit(code=1)

                # Save each page as PNG with nested progress bar
                for page_num, image in enumerate(
                    tqdm(
                        images,
                        desc=f"  Pages in {pdf_file.name}",
                        unit="page",
                        leave=False,
                    ),
                    start=1,
                ):
                    # Create filename: original_name_page_N.png
                    png_filename = f"{pdf_file.stem}_page_{page_num}.png"
                    png_path = temp_dir / png_filename
                    image.save(str(png_path), "PNG")
                    png_paths.append(png_path)

            except ImportError:
                tqdm.write(
                    "Error: poppler is required for PDF conversion.\n"
                    "Please install it:\n"
                    "  macOS: brew install poppler\n"
                    "  Ubuntu/Debian: sudo apt-get install poppler-utils\n"
                    "  Windows: Download from "
                    "https://github.com/oschwartz10612/poppler-windows/releases/"
                )
                raise typer.Exit(code=1) from None
            except OSError as e:
                error_msg = str(e).lower()
                if "poppler" in error_msg or "pdftoppm" in error_msg:
                    tqdm.write(
                        "Error: poppler is not installed or not in PATH.\n"
                        "Please install it:\n"
                        "  macOS: brew install poppler\n"
                        "  Ubuntu/Debian: sudo apt-get install poppler-utils\n"
                        "  Windows: Download from "
                        "https://github.com/oschwartz10612/poppler-windows/releases/"
                    )
                else:
                    tqdm.write(f"Error: Failed to read {pdf_file.name}: {e}")
                raise typer.Exit(code=1) from None
            except Exception as e:
                tqdm.write(f"Error: Failed to convert {pdf_file.name}: {e}")
                raise typer.Exit(code=1) from None

    return natsorted(png_paths)


def create_presentation(png_files: list[Path], output_path: Path) -> None:
    """Create a PowerPoint presentation with one PNG per slide.

    Args:
        png_files: List of PNG file paths to add to the presentation.
        output_path: Path where the PowerPoint file should be saved.

    Raises:
        typer.Exit: If there's an error creating the presentation or saving the file.
    """
    try:
        prs = Presentation()
        prs.slide_width = Inches(10)  # 16:9 aspect ratio
        prs.slide_height = Inches(5.625)

        blank_slide_layout = prs.slide_layouts[6]  # Blank layout

        # Progress bar for slide creation
        for png_file in tqdm(png_files, desc="Creating slides", unit="slide"):
            try:
                slide = prs.slides.add_slide(blank_slide_layout)

                # Calculate image dimensions to fit slide while maintaining aspect ratio
                left = Inches(0)
                top = Inches(0)
                width = prs.slide_width
                height = prs.slide_height

                slide.shapes.add_picture(
                    str(png_file), left, top, width=width, height=height
                )
            except Exception as e:
                tqdm.write(f"Error: Failed to add image {png_file.name}: {e}")
                raise typer.Exit(code=1) from None

        prs.save(str(output_path))
    except PermissionError:
        tqdm.write(f"Error: Permission denied writing to {output_path}")
        raise typer.Exit(code=1) from None
    except OSError as e:
        tqdm.write(f"Error: Failed to save presentation to {output_path}: {e}")
        raise typer.Exit(code=1) from None


@app.command()
def main(
    input_path: Path = typer.Argument(
        ...,
        help="Path to a PNG/PDF file or folder containing PNG/PDF files",
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
    ),
    output_file: Path = typer.Argument(
        ...,
        help="Path for output PowerPoint file (e.g., output.pptx)",
    ),
    dpi: int = typer.Option(
        400,
        help="DPI for PDF to PNG conversion (50-2000, higher = better quality)",
        min=50,
        max=2000,
    ),
) -> None:
    """Convert PNG or PDF file(s) into a PowerPoint presentation.

    Accepts either a single file or a folder containing multiple files.
    Each PNG file or PDF page becomes one slide in the presentation.
    Files are ordered using natural sort (e.g., image1, image2, image10).

    For PDF files, each page is converted to a PNG at the specified DPI before
    being added to the presentation.
    """
    # Validate output file extension
    if output_file.suffix.lower() != ".pptx":
        typer.echo("Error: Output file must have .pptx extension", err=True)
        raise typer.Exit(code=1)

    # Validate output directory exists and is writable
    output_dir = output_file.parent
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            typer.echo(
                f"Error: Cannot create output directory {output_dir}: {e}", err=True
            )
            raise typer.Exit(code=1) from None

    if not output_dir.is_dir():
        typer.echo(f"Error: {output_dir} is not a directory", err=True)
        raise typer.Exit(code=1)

    # Check if output file already exists and warn user
    if output_file.exists():
        typer.echo(f"Warning: {output_file} already exists and will be overwritten")

    # Detect if input is a file or folder and gather files to process
    temp_dir: Path | None = None
    png_files: list[Path] = []

    try:
        if input_path.is_file():
            # Single file mode
            file_type, files = process_single_file(input_path)
            if file_type == FileType.PNG:
                typer.echo(f"Processing single PNG file: {input_path.name}")
                png_files = files
            else:
                typer.echo(f"Processing single PDF file: {input_path.name}")
                # Create temporary directory
                temp_dir = Path(tempfile.mkdtemp(prefix="png_to_ppt_"))
                # Convert PDF to PNGs
                png_files = convert_pdf_to_pngs(files, dpi, temp_dir)
        else:
            # Folder mode
            file_type = detect_file_type(input_path)
            if file_type == FileType.PNG:
                # PNG mode: use files directly
                png_files = find_png_files(input_path)
                typer.echo(f"Found {len(png_files)} PNG file(s)")
            else:
                # PDF mode: convert to PNGs in temp directory
                pdf_files_list = find_pdf_files(input_path)
                typer.echo(f"Found {len(pdf_files_list)} PDF file(s)")
                # Create temporary directory
                temp_dir = Path(tempfile.mkdtemp(prefix="png_to_ppt_"))
                # Convert PDFs to PNGs
                png_files = convert_pdf_to_pngs(pdf_files_list, dpi, temp_dir)

        # Create presentation
        create_presentation(png_files, output_file)

        typer.echo(f"✓ Successfully created {output_file}")

    finally:
        # Cleanup temporary directory if it was created
        if temp_dir and temp_dir.exists():
            shutil.rmtree(temp_dir)
            typer.echo("Cleaned up temporary files")


if __name__ == "__main__":
    app()
