# имена классов должны начинаться с sf_
# и отображать основные характеристики (по усмотрению разработчика)

import os
import io
from abc import ABC, abstractmethod
from langchain.docstore.document import Document as LangDocument

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
    
class sf_add_keywords_512_chunk:
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

        print ("start sf_add_keywords_512_chunk")

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

        doc_c = get_keywords(documents)
        keywords = doc_c.get_keywords_def()
        print (keywords)
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=50,)
        chunks = text_splitter.split_documents(documents)
        enriched_chunks = [doc_c.enrich_chunk_with_additional_info(chunk, keywords) for chunk in chunks]

        print ("finish sf_add_keywords_512_chunk")
        return enriched_chunks

class get_keywords:
    
    from typing import List
    from langchain_ollama import OllamaLLM
    
    promt_category = {
        "Закон или нормативный акт": (
            {"Номер закона или нормативного акта " : "Какой номер документа?",
             "Наименование закона или нормативного акта " : "Какое наименование документа?",
             "Дата закона или нормативного акта " : "Какая дата документа?"}
        ),
        "Договор": (
            {"Номер договора ":"Какой номер договора?",
             "Дата заключения договора ":"Какая дата договора?",
             "Договор заключен между ":" Между кем заключен договор?",
             "Предмет договора ":"Какой предмет договора?"}
        ),
        "Письмо": (
            {"Письмо от ":"Кто написал письмо?",
            "Дата письма ":"Какая дата письма?",
            "Получатель письма " : "Кто получатель письма?",
            "Тема письма " : "Какая тема письма ?"}
        ),
        "Курсовая или дипломная работа": (
            {"Тема курсовой или дипломной работы ":"Какая тема работы?",
            "Автор курсовой или дипломной работы ":"Кто подготовил работу?"}
        ),
        "Информация об организации": (
            {"Наименование организации ":" Какое наименование организации?"}
        ),
        "Техническое задание или технический проект": (
            {"Наименование технического задания ":"Какое наименование документа?",
            "Номер технического задания ":"Какой номер документа?",
            "Автор технического задания ": "Кто подготовил документ?"}
        ),
        "Рассказ или повесть": (
            {"Автор художественного произведения ": "Кто автор документа?", 
            "Название произведения": "Какое название документа?"}
        ),
        "Неизвестная категория": (
            {}
        )
    }
    X_char = 1000
    llm_class = OllamaLLM(model="deepseek-r1:latest", temperature = "0.1")
    llm_keywords = OllamaLLM(model="llama3:latest", temperature = "0.0")
    
    def __init__(self, documents: List[LangDocument]):
        self.documents = documents
    
    def remove_text_between_tags(self, text: str):
        start_tag = '<think>'
        end_tag = '</think>'

        result = []
        last_position = 0

        while True:
            start_index = text.find(start_tag, last_position)
            if start_index == -1:
                break

            result.append(text[last_position:start_index])

            end_index = text.find(end_tag, start_index + len(start_tag))
            if end_index == -1:
                break

            last_position = end_index + len(end_tag)

        result.append(text[last_position:])

        return ''.join(result)
    
        
    def clean_doc(self):
        """
        Заменяет все символы перевода строки в page_content у каждого документа.
        """
        for doc in self.documents:
            doc.page_content = doc.page_content.replace('\n', '')

    def get_X_characters(self) -> str:
        """
        Возвращает X символов из списка документов, объединяя page_content.
        """
#         result = ""
#         for doc in self.documents:
#             if len(result) >= self.X_char:
#                 break
#             result += doc.page_content[:self.X_char - len(result)]
#         return result
        result_start = ""
        result_end = ""

        # Собираем X символов с начала списка
        for doc in self.documents:
            if len(result_start) >= self.X_char:
                break
            result_start += doc.page_content[:self.X_char - len(result_start)]

        # Собираем X символов с конца списка (начиная с конца)
        for doc in reversed(self.documents):
            if len(result_end) >= self.X_char:
                break
            result_end = doc.page_content[-(self.X_char - len(result_end)):] + result_end

        return result_start + result_end

    def define_document_type(self, doc_for_context: str) -> str:
        """
        Определение типа документа.
        """
        category_str = ""

        for category, promt in self.promt_category.items():
            category_str = category_str + category + ", "
        promt_category = f"""Контекст: мы проводим работы по классификации текстов, необходимо определять к какой категории относится текст
        Роль: твоя роль по части текста определять к какой из предложенных категории относится этот текст 
        Задача: Тебе предоставлен текст {doc_for_context} ты должен определить к какой  
        категорий из списка он относится, список категорий: {category_str}. 
        Критерии Качества: необходимо предоставить точно одну из предоставленных списка категорий, нельзя менять использовать другие слова, должно быть только название категории"""
        llm_response = self.llm_class.invoke(promt_category)
        return self.remove_text_between_tags(llm_response)

            
    def find_category(self, text: str) -> str:
        """
        Определяет категорию текста на основе словаря promt_category.
        """
        for category in self.promt_category.keys():
            if category.lower() in text.lower():
                return category
        return "Неизвестная категория"
    
    def return_promt_find_keywords(self, doc_type: str) -> str:
        """
        Возвращает промт для поиска ключевых слов.
        """
        promt_ = ""
        dictionary = self.promt_category
        if doc_type in dictionary:
            promt_ =  dictionary[doc_type]
        
        return promt_
    
    def find_keywords(self, input_dic, doc_char: str) -> str:
        """
        Возвращает ключевые слова.
        """ 
        promt_keyword = "Вы полезный ассистент. Вы отвечаете на вопросы о документации, используя эти данные: {self.data}. Ответь на русском языке на этот запрос: {self.prompt} "
        promt_keyword = promt_keyword.replace("{self.data}", doc_char)
            
        #parts = input_str.split(";")  # Разделяем строку по ";"
        modified_parts = []  # Создаем список для измененных частей

        for key in input_dic:
            promt_llm = promt_keyword.replace("{self.prompt}", input_dic[key])
            llm_response = self.llm_keywords.invoke(promt_llm)
            modified_parts.append(key + " " + llm_response)  

        return ";".join(modified_parts)  # Объединяем обратно в строку


        #llm_response = self.llm_pd.invoke(promt_keyword)
        #return self.remove_text_between_tags(llm_response)
    
    def add_keywords(self, additional_info: str):
        """
        Добавляет ключевое слово в page_content каждого документа под ключом 'keywords'.
        """
        for doc in self.documents:
            if 'page_content' not in doc.__dict__:
                doc.page_content = ""
            doc.page_content += f"\n\n{additional_info}"
    
    def get_keywords_def(self):
        self.clean_doc()
        doc_char = self.get_X_characters()
        doc_type_llm = self.define_document_type(doc_char)
        doc_type = self.find_category(doc_type_llm)
        promt_key = self.return_promt_find_keywords(doc_type)
        return self.find_keywords(promt_key, doc_char)
    
    def enrich_chunk_with_additional_info(self, doc, additional_text):
        """Добавляет additional_info в текст чанка, но не объединяет все метаданные"""
        enriched_content = f"{additional_text}\n\n{doc.page_content}"  # 👈 Добавляем только `additional_info`
        return LangDocument(page_content=enriched_content, metadata=doc.metadata)
    