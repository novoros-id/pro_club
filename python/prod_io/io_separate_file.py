# имена классов должны начинаться с sf_
# и отображать основные характеристики (по усмотрению разработчика)

class sf_default:
    def __init__(self, file_path):
        self.file_path = file_path
    def separate_file(self):
        import os
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_community.document_loaders import Docx2txtLoader
        from langchain.text_splitter import (
            RecursiveCharacterTextSplitter,
        )
        basename, extension = os.path.splitext(self.file_path)

        match extension:
            case ".docx":
                loader = Docx2txtLoader(self.file_path)
            case ".pdf":  
                loader = PyPDFLoader(self.file_path)
            case _:
                print(f"Данный файл не поддерживается {self.file_path}")
                return []

        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200,)
        documents = text_splitter.split_documents(documents)

        return documents
    
class sf_500_100_podg:
    def __init__(self, file_path):
        self.file_path = file_path
    def separate_file(self):
        import os
        import re 
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_community.document_loaders import Docx2txtLoader
        from langchain.text_splitter import (
            RecursiveCharacterTextSplitter,
        )
        basename, extension = os.path.splitext(self.file_path)

        match extension:
            case ".docx":
                loader = Docx2txtLoader(self.file_path)
            case ".pdf":  
                loader = PyPDFLoader(self.file_path)
            case _:
                print(f"Данный файл не поддерживается {self.file_path}")
                return []

        documents = loader.load()

        # pages = []
        # for doc in documents:
        #     cleaned_document = doc.replace('\n', '')
        #     pages.append(cleaned_document)

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100,)
        documents = text_splitter.split_documents(documents)

        return documents