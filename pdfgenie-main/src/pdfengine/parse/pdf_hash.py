import hashlib
import os

class PDFHasher:
    def __init__(self, pdf_file):
        self.pdf_file = pdf_file

    def get_hash(self):
        hash_md5 = hashlib.md5()
        with open(self.pdf_file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

if __name__ == "__main__":
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.realpath(__file__))
    print(current_dir)
    pdf_file = current_dir.replace("src/pdfengine/parse", "pdfs/10103549.pdf")
    hasher = PDFHasher(pdf_file)
    print(hasher.get_hash())