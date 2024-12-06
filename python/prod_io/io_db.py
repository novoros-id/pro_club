import os
import io_file_operation

from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
)
from langchain.embeddings  import HuggingFaceEmbeddings

from langchain.vectorstores import Chroma
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction
from chromadb.config import Settings

from langchain_ollama import OllamaLLM
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain import PromptTemplate
from langchain.schema import HumanMessage


class DbHelper:

    def __init__(self, chat_id, user_name):
        self.chat_id = chat_id
        self.user_name = user_name

    def processing_user_files(self):

        pdf_files_list = self.get_all_user_files()

        if len(pdf_files_list) == 0:
            #todo show user error
            return
        
        for file_item in pdf_files_list:
            separate_text = self.separate_file(file_item)
            embedding = self.get_embeddings_from_separate_text(separate_text)
            self.put_vector_in_db(separate_text, embedding)

    def get_all_user_files(self):

        user_folder_path = io_file_operation.return_user_folder(self.user_name)
        if not os.path.exists(user_folder_path):
            return []
        
        pdf_folder = os.path.join(user_folder_path, 'pdf')

        if not os.path.exists(pdf_folder):
            return []
        
        pdf_files_all = [os.path.join(pdf_folder, file) for file in os.listdir(pdf_folder)]

        return pdf_files_all

    def separate_file(self, file_path):

        loader = PyPDFLoader(file_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200,)
        documents = text_splitter.split_documents(documents)

        return documents

    def get_embeddings_from_separate_text(self, separate_text):

        hf_embeddings_model = HuggingFaceEmbeddings(
            #todo: need parametr for model_kwargs
        model_name="cointegrated/LaBSE-en-ru", model_kwargs={"device": "cpu"})

        return hf_embeddings_model

    def put_vector_in_db(self, separate_text, embedding):

        user_folder_path = io_file_operation.return_user_folder(self.user_name)
        if not os.path.exists(user_folder_path):
            return False
        
        db_folder = os.path.join(user_folder_path, 'db')

        if not os.path.exists(db_folder):
            return False

        vector_db = Chroma.from_documents(
            documents=separate_text,
            embedding=embedding,
            persist_directory=db_folder,
            )
        
        return True

    def get_vectror_db(self):

        user_folder_path = io_file_operation.return_user_folder(self.user_name)
        if not os.path.exists(user_folder_path):
            return False
        
        db_folder = os.path.join(user_folder_path, 'db')

        if not os.path.exists(db_folder):
            return False
        
        '''
        model_llm = OllamaEmbeddingFunction(
            url="http://localhost:11434/api/embeddings",
            model_name="llama3",
            )
        '''
        #todo: need parametr for model_kwargs
        hf_embeddings_model = HuggingFaceEmbeddings(
            model_name="cointegrated/LaBSE-en-ru", model_kwargs={"device": "cpu"})

        vectordb = Chroma(persist_directory=db_folder, embedding_function=hf_embeddings_model)

        return vectordb

    def get_answer(self, prompt):

        vectordb = self.get_vectror_db()

        llm = OllamaLLM(
<<<<<<< HEAD
            model="llama3",  temperature = "0.1")
=======
            model="llama3", temperature = "0.1")
>>>>>>> 8e38881 (123)

        #print(dir(vectordb))
        data = vectordb.similarity_search(prompt,k=4)
        #embedding_vector  = OllamaLLM().embed_query(prompt) 
        #data = vectordb.similarity_search_by_vector(embedding_vector)
        question = f"Используя эти данные: {data}. Ответь на русском языке на этот запрос: {prompt} и укажи source "
        text = llm.invoke([HumanMessage(content=question)])

        return text
