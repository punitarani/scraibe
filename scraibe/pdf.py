"""scraibe.pdf.py"""

from pathlib import Path

from fitz import fitz


def pdf_to_txt(pdf_fp: Path, txt_fp: Path) -> Path:
    """
    Convert a PDF file to a text file.

    Parameters
    ----------
    pdf_fp : Path
        The filepath to the PDF file.
    txt_fp : Path
        The filepath to the text file.

    Returns
    -------
    Path
        The filepath to the text file.
    """

    # Open the PDF file
    with fitz.open(pdf_fp) as doc:
        # Convert the PDF file to a text file
        text = ""
        for page in doc:
            text += page.get_text()

    # Save the text file with UTF-8 encoding
    with txt_fp.open("w", encoding="utf-8") as buffer:  # Specify encoding here
        buffer.write(text)

    return txt_fp
