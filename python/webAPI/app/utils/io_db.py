import os
import base64
from typing import Optional, Union, Type, List
from enum import Enum
import json
from dataclasses import dataclass, field
#import io_file_operation
#import io_json
from app.utils.llm_implementation import io_separate_file
import app.utils.llm_implementation.io_embeddings as io_embeddings
import app.utils.llm_implementation.io_put_vector_in_db as io_put_vector_in_db
import app.utils.llm_implementation.io_get_vectror_db as io_get_vectror_db
import app.utils.llm_implementation.io_search_from_db as io_search_from_db
import app.utils.llm_implementation.io_promt as io_promt
import app.utils.io_file_operation as io_file_operation

from app.config import settings_llm, settings

from langchain_ollama import OllamaLLM
from langchain.schema import HumanMessage

class LLM_Models(Enum):
    Olama3 = settings_llm.MODEL

@dataclass
class Processed_Files:
    name: str

@dataclass
class Prompts:
    text: str

@dataclass
class ConfigLLM:
    processed_files: List[Processed_Files] = field(default_factory=list) 
    prompts: List[Prompts] = field(default_factory=list) 

    def to_dict(self):
        return {
           "processed_files": [file.__dict__ for file in self.processed_files],
           "prompts": [texts.__dict__ for texts in self.prompts]}
    
    @classmethod
    def from_dict(cls, data: dict):
        processed_files = [Processed_Files(**files) for files in data["processed_files"]]
        prompts = [Prompts(**texts) for texts in data["prompts"]]
        return cls(processed_files=processed_files, prompts=prompts)


#---------------------------------------------------
class DbHelper:

    def __init__(self, user_name, default_model: LLM_Models = LLM_Models.Olama3):
        #self.chat_id = chat_id
        self.user_name = user_name
        self.default_model= default_model
        
    """def process_files(self, user_name):
        copy_user_files_from_input(user_name)
        db_helper = io_db.DbHelper(user_name)
        self.processing_user_files() """

    def processing_user_files(self, processing_all_files: Optional[bool]=False, saved_files = []):
        print("Start processing_user_files")
        print ("файлов для обработки")
        print(len(saved_files))
        configLLM_object = self.get_configLLM_file()

        all_pdf_file_list = self.get_all_user_files()
        if processing_all_files:
            pdf_files_list = all_pdf_file_list
            files_to_update = []
            configLLM_object.processed_files.clear
        else:
            # get differents between all user files and processed files
            set_difference = set(all_pdf_file_list) - set([file.name for file in configLLM_object.processed_files])
            pdf_files_list = list(set_difference)

            # Если файлы были добавлены ранее, то добавим в словарь повторной загрузки
            user_folder_path = io_file_operation.return_user_folder(self.user_name)
            user_folder_path = os.path.join(user_folder_path, 'pdf') 
            files_to_update = list(map(lambda file: os.path.join(user_folder_path, file), saved_files))
            print ("файлов для обновления")
            print(len(files_to_update))

        if len(pdf_files_list) == 0 and len(files_to_update) == 0:
            #todo show user error
            return
        
        self.clear_files_in_db(files_to_update)
        pdf_files_list = pdf_files_list + files_to_update
        
        for file_item in pdf_files_list:
            separate_text = self.separate_file(file_item)
            embedding = self.get_embeddings()
            self.put_vector_in_db(separate_text, embedding)
            #check file as processed
            configLLM_object.processed_files.append(Processed_Files(name=file_item))
    
        #save configLLM
        self.save_to_configLLM_file(configLLM_object)
        print("finish processing_user_files")

    def get_configLLM_file(self):
        user_folder_path = io_file_operation.return_user_folder(self.user_name)
        configLLM_full_path = os.path.join(user_folder_path, 'configLLM.json')
        configLLM_object = ConfigLLM()
        if not os.path.exists(configLLM_full_path):
            # create confilLLM file
           with open(configLLM_full_path, 'w') as file:
                json.dump(configLLM_object.to_dict(), file, indent=4)
         
        with open(configLLM_full_path, 'r') as file:
            data = json.load(file)
            configLLM_object = configLLM_object.from_dict(data)

        return configLLM_object
        
    def save_to_configLLM_file(self, configLLM_object: ConfigLLM):
        user_folder_path = io_file_operation.return_user_folder(self.user_name)
        configLLM_full_path = os.path.join(user_folder_path, 'configLLM.json')
        if not os.path.exists(configLLM_full_path):
            return
        
        with open(configLLM_full_path, 'w') as file:
            json.dump(configLLM_object.to_dict(), file, indent=4)

    def delete_all_user_db(self):
        #db_user_files = io_file_operation.return_user_folder_db(self.user_name)
        #io_file_operation.delete_all_files_in_folder(self.chat_id, db_user_files, True)
        vectordb = self.get_vectror_db()
        vectordb._client.delete_collection("main")
        self.delete_proocessed_files_in_config()

    def delete_proocessed_files_in_config(self):
        user_folder_path = io_file_operation.return_user_folder(self.user_name)
        configLLM_full_path = os.path.join(user_folder_path, 'configLLM.json')
        configLLM_object = ConfigLLM()
        if os.path.exists(configLLM_full_path):
            # create confilLLM file
           with open(configLLM_full_path, 'w') as file:
                json.dump(configLLM_object.to_dict(), file, indent=4)


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

        class_name_separate_file = settings_llm.CLASS_NAME_SEPARATE_FILE
        separate_class = getattr(io_separate_file, class_name_separate_file)
        separate_object = separate_class(file_path)
        return separate_object.separate_file()

    def get_embeddings(self):

        class_name_embedings = settings_llm.CLASS_NAME_EMBEDDINGS
        embedings_class = getattr(io_embeddings, class_name_embedings)
        embedings_object = embedings_class()
        return embedings_object.get_embeddings()

    def put_vector_in_db(self, separate_text, embedding):
        class_name_pvidb = settings_llm.CLASS_NAME_PUT_VECTOR_IN_DB
        pvidb_class = getattr(io_put_vector_in_db, class_name_pvidb)
        pvid_object = pvidb_class(separate_text, embedding, self.user_name)
        return pvid_object.put_vector_in_db()
    
    def clear_files_in_db(self, files_to_update):
        for files in files_to_update:
            print("Обновляю файл")
            print(files)
            vector_db = self.get_vectror_db()
            print("ищу данные в базе")
            docs_to_delete = vector_db.get(where={"source": files})
            for doc_id, metadata in zip(docs_to_delete["ids"], docs_to_delete["metadatas"]):
                print(f"ID: {doc_id}, Metadata: {metadata}")
                vector_db.delete(ids=doc_id)
            print("Документы успешно удалены!")

    def get_vectror_db(self):

        class_name_gvidb = settings_llm.CLASS_NAME_GET_VECTOR_DB
        gvidb_class = getattr(io_get_vectror_db, class_name_gvidb)
        gvid_object = gvidb_class(self.user_name)
        return gvid_object.get_vectror_db() 

    def get_answer(self, prompt, llm_model: LLM_Models = None):

        vectordb = self.get_vectror_db()

        selected_llm_model = llm_model if llm_model else self.default_model

        if selected_llm_model == LLM_Models.Olama3:
            llm = OllamaLLM(
                model=selected_llm_model, temperature = "0.1")
        else:
            return 'Бот не поддерживает модель ({})'.format(llm_model.name)

        #print(dir(vectordb))

        class_name_search = settings_llm.CLASS_NAME_SEARCH
        search_class = getattr(io_search_from_db, class_name_search)
        search_object = search_class(prompt, self.user_name, vectordb)
        data =  search_object.seach_from_db()

        #data = vectordb.similarity_search(prompt,k=4)
        #embedding_vector  = OllamaLLM().embed_query(prompt) 
        #data = vectordb.similarity_search_by_vector(embedding_vector)
        #Вы полезный ассистент. Вы отвечаете на вопросы о документации, хранящейся в
        #question = f"Используя эти данные: {data}. Ответь на русском языке на этот запрос: {prompt} и укажи source "
        #question = f"Вы полезный ассистент. Вы отвечаете на вопросы о документации, используя эти данные: {data}. Ответь на русском языке на этот запрос: {prompt} и укажи source "

        class_name_promt = settings_llm.CLASS_NAME_PROMT
        promt_class = getattr(io_promt, class_name_promt)
        promt_object = promt_class(data, prompt)
        question  =  promt_object.get_promt()

        text = llm.invoke([HumanMessage(content=question)])

        return text
    
    def get_free_answer (self, prompt, llm_model: LLM_Models = None):
        
        selected_llm_model = llm_model if llm_model else self.default_model

        encoded_credentials = base64.b64encode(f"{settings_llm.USER_LLM}:{settings_llm.PASSWORD_LLM}".encode()).decode()
        headers = {'Authorization': f'Basic {encoded_credentials}'}
        
        if selected_llm_model == LLM_Models.Olama3:
            llm = OllamaLLM(
                model=selected_llm_model, temperature = "0.1", base_url=settings_llm.URL_LLM, client_kwargs={'headers': headers})
        else:
            return 'Бот не поддерживает модель ({})'.format(llm_model.name)
        
        question = f"Вы полезный ассистент. Вы отвечаете на вопросы пользователей. Ответь на русском языке на этот запрос: {prompt} Отвечай коротко и по делу "

        try:
            text = llm.invoke([HumanMessage(content=question)])
        except Exception as e:
              print(f"Произошла ошибка: {str(e)}")
        
        '''
        model_name = "cointegrated/LaBSE-en-ru"
        model = SentenceTransformer(model_name)
        question = [prompt]
        embedings = model.encode(question)
  
        llm = OllamaLLM(
                model=embedings, temperature = "0.1")
        
        text = llm.invoke([HumanMessage(content=question)])
        '''
        return text
        
        

