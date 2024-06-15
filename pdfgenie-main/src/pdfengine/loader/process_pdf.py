from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain_community.document_loaders import PDFMinerPDFasHTMLLoader
from langchain_community.docstore.document import Document
from typing import Any
import pymupdf4llm
from bs4 import BeautifulSoup
import pymupdf
from functools import partial
import re
from .cleaners.utils import basic_cleaner, remove_images, remove_duplicates
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document

class UnstructuredPDFProcessor(object):
    def __init__(self, file_path):
        self.loader = UnstructuredPDFLoader(file_path=file_path, mode="single")
        self.document = None

    def process_pdf(self):
        self.document = self.loader.load()
        return self.document


class PDFMinerPDFasHTMLProcessor(object):
    def __init__(self, pdf_path):
        self.loader = PDFMinerPDFasHTMLLoader(pdf_path)
        self.data = self.loader.load()[0]
        self.soup = BeautifulSoup(self.data.page_content, "html.parser")
        self.content = self.soup.findAll("div")
        self.snippets: list[tuple] = []
        self.semantic_snippets: list[Document] = []

    def process_pdf(self):
        cur_fs = None
        cur_text = ""
        # snippets = []   # first collect all snippets that have the same font size
        for c in self.content:
            sp = c.find("span")
            if not sp:
                continue
            st = sp.get("style")
            if not st:
                continue
            fs = re.findall("font-size:(\d+)px", st) # type: ignore
            if not fs:
                continue
            fs = int(fs[0])
            if not cur_fs:
                cur_fs = fs
            if fs == cur_fs:
                cur_text += c.text
            else:
                self.snippets.append((cur_text, cur_fs))
                cur_fs = fs
                cur_text = c.text
        self.snippets.append((cur_text, cur_fs))
        cur_idx = -1
        semantic_snippets = []
        # Assumption: headings have higher font size than their respective content
        for s in self.snippets:
            # if current snippet's font size > previous section's heading => it is a new heading
            if (
                not semantic_snippets
                or s[1] > semantic_snippets[cur_idx].metadata["heading_font"]
            ):
                metadata = {"heading": s[0], "content_font": 0, "heading_font": s[1]}
                metadata.update(self.data.metadata)
                semantic_snippets.append(Document(page_content="", metadata=metadata))
                cur_idx += 1
                continue

            # if current snippet's font size <= previous section's content => content belongs to the same section (one can also create
            # a tree like structure for sub sections if needed but that may require some more thinking and may be data specific)
            if (
                not semantic_snippets[cur_idx].metadata["content_font"]
                or s[1] <= semantic_snippets[cur_idx].metadata["content_font"]
            ):
                semantic_snippets[cur_idx].page_content += s[0]
                semantic_snippets[cur_idx].metadata["content_font"] = max(
                    s[1], semantic_snippets[cur_idx].metadata["content_font"]
                )
                continue

            # if current snippet's font size > previous section's content but less than previous section's heading than also make a new
            # section (e.g. title of a PDF will have the highest font size but we don't want it to subsume all sections)
            metadata = {"heading": s[0], "content_font": 0, "heading_font": s[1]}
            metadata.update(self.data.metadata)
            semantic_snippets.append(Document(page_content="", metadata=metadata))
            cur_idx += 1
        self.semantic_snippets = semantic_snippets
        return self.semantic_snippets


class PyMuPDFProcessor(object):
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.doc = pymupdf.open(pdf_path)
        self.images = []
        self.tables = []
        self.text = []
        self.graphics = []
        self.table_metadata = []

    def get_text(self):
        pass

    def find_tables(self):
        pass


class PDFMarkdownProcessor(object):
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.pages = pymupdf4llm.to_markdown(
            pdf_path, page_chunks=True, write_images=False
        )
        if len(self.pages) == 0:
            raise ValueError("No content found in the pdf")
        try:
            self.doc_metadata = self.extract_metadata(self.pages[0].metadata)  # type: ignore
        except (AttributeError, IndexError):
            self.doc_metadata = None
        self.page_text = [p["text"] for p in self.pages]  # type: ignore
        if self.doc_metadata:
            md_metadata = ""
            for k, v in self.doc_metadata.items():
                md_metadata += f"{k}: {v}\n"
            self.page_text[0] = f'{md_metadata}\n{self.page_text[0]}'
        self.page_text = self.clean_text()
        self.documents = self.make_documents()
        

    @staticmethod
    def extract_metadata(metadata: dict[str, str]):
        metadata_keys = [
            "title",
            "author",
            "subject",
            "keywords",
            "creator",
        ]
        metadata_dict = {}
        for key in metadata_keys:
            try:
                metadata_dict[key] = metadata.get(key)
            except KeyError:
                metadata_dict[key] = None
        return metadata_dict

    def clean_text(self):
        self.page_text = [basic_cleaner(p) for p in self.page_text]  # type: ignore
        self.page_text = [remove_images(p) for p in self.page_text]  # type: ignore
        # self.page_text = [remove_duplicates(p) for p in self.page_text]  # type: ignore
        return self.page_text

    def make_documents(self):
        documents = []
        for i, page in enumerate(self.page_text):
            documents.append(Document(page_content=page, metadata={"page_number": i}))
        return documents

    def get_documents(self):
        return self.documents


if __name__ == "__main__":
    # pdf_path = '/Users/devika/Desktop/pdfgenie/pdfs/BDCC-07-00097-v3.pdf'
    # processor = PDFMinerPDFasHTMLProcessor(pdf_path)
    # processor = UnstructuredPDFProcessor(pdf_path)
    # document = processor.process_pdf()
    # for s in document:
    #     print(s)
    pdf_path = '/Users/devika/Desktop/pdfgenie/src/pdfengine/setup/test.pdf'
    processor = PDFMarkdownProcessor(pdf_path)
    documents = processor.get_documents()
    for doc in documents:
        print(doc.page_content)
