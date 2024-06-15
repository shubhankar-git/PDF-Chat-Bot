import sys
sys.path.append("src")
from pdfengine.parse.pdf_hash import PDFHasher # type: ignore
import requests

def test_pdf_hash():
    hasher = PDFHasher("pdfs/10103549.pdf")
    assert hasher.get_hash() == "aca93d6426f73c52c4d3539ecb242e5b"