from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.documents import Document
from .retrieve import RetrievalChain

class Genie(object):
    def __init__(self, open_api_key_, model_, file_path=None):
        self.open_api_key = open_api_key_
        self.model = model_
        self.chat_history = []
        if file_path:
            self.file_path = file_path
        else:
            raise Exception("File path is required to prepare the retrieval chain")
        # self.retrieval_chain
    
    def prepare_chain(self):
        rc = RetrievalChain(open_api_key_=self.open_api_key, model_=self.model, file_path=self.file_path)
        return rc.prepare_the_retrieval_chain()
         
    
    def save_input(self, input_):
        h = HumanMessage(content=input_)
        self.chat_history.append(h)
        return
    
    def save_genie_response(self, genie_):
        genie = AIMessage(content=genie_)
        self.chat_history.append(genie)
        return
    
    def take_input(self):
        i = input("chat with Genie:")
        self.save_input(i)
        return i

    def genies_responses(self, input_, retrieval_chain_):

        response = retrieval_chain_.invoke({
                "chat_history": [],
                "input": input_,
            })
        
        self.save_genie_response(response['answer'])
        return response

    
    def chat_with_the_genie(self):
        rc = self.prepare_chain()    
        i = self.take_input()

        while(i!="e"):
            response = self.genies_responses(i, rc)
            print(response['answer'])

            i = self.take_input()                
        
        print(self.chat_history)
        return


if __name__ == "__main__":
    a="sk-proj-q8LIi1ONH9ZFfjC4ANWLT3BlbkFJWYG7sprgE8S3LzWxlmjx"
    m="gpt-3.5-turbo"
    G = Genie(open_api_key_=a, model_=m, file_path="/Users/devika/Desktop/pdfgenie/src/pdfengine/loader/test.pdf")
    G.chat_with_the_genie()
    

