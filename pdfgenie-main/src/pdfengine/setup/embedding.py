# from "./../loader/process_pdf" import PDFMarkdownProcessor
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from ..loader.process_pdf import PDFMarkdownProcessor

class VectorRetriever(object):
    def __init__(self, open_api_embedding_key_, file_path, embedding_model=None):
        self.open_api_embedding_key = open_api_embedding_key_
        if embedding_model is not None:
            self.open_api_embedding_model = embedding_model
        else:
            self.open_api_embedding_model = "text-embedding-3-large"
        self.file_path = file_path
        self.open_api_embedding = self.give_openai_embedding_object()
        self.documents = self.give_the_document_object()
        self.vectors = self.prepare_the_vectors()
        self.retriever = self.prepare_the_retriever()

    def give_openai_embedding_object(self): # gives OpenAIEmbedding object
        return OpenAIEmbeddings(api_key=self.open_api_embedding_key,model=self.open_api_embedding_model) # type: ignore

    def give_the_document_object(self):
        # give the document object to pass to the FAISS.from_document method to embedd the document and store in FAISS as vectors
        # temporary Document generating code:
        loader = PDFMarkdownProcessor(self.file_path)
        self.documents =  loader.get_documents()
        return self.documents

    def prepare_the_vectors(self):
        return FAISS.from_documents(self.documents,self.open_api_embedding)

    def prepare_the_retriever(self):         # to dynamically select the most relevant documents and pass those in for a given question.
        vector = self.prepare_the_vectors()
        return vector.as_retriever()