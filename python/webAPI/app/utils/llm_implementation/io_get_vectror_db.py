# имена классов должны начинаться с gvid_
# и отображать основные характеристики (по усмотрению разработчика)

class gvid_default:
    def __init__(self, user_name):
        self.user_name = user_name
    def get_vectror_db(self):

        #import app.services.file_service as file_service
        import os
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_chroma import Chroma

        # временно для запуска конвейра
        import importlib

        print("Тип self.user_name")
        print(type(self.user_name))

        if isinstance(self.user_name, str):
            module_name = "pipeline.io_file_operation"
        else:
            module_name = "app.utils.io_file_operation"
        
        io_file_operation = importlib.import_module(module_name)
        # временно для запуска конвейра

        user_folder_path = io_file_operation.return_user_folder(self.user_name)
        if not os.path.exists(user_folder_path):
            return False
        
        db_folder = os.path.join(user_folder_path, 'db')

        if not os.path.exists(db_folder):
            return False
        
        #todo: need parametr for model_kwargs
        hf_embeddings_model = HuggingFaceEmbeddings(
            model_name="cointegrated/LaBSE-en-ru", model_kwargs={"device": "cpu"})

        vectordb = Chroma(collection_name = "main", persist_directory=db_folder, embedding_function=hf_embeddings_model)

        return vectordb

class gvid_multilingual_e5_large:
    def __init__(self, user_name):
        self.user_name = user_name
    def get_vectror_db(self):

        print ("start gvid_multilingual_e5_large")
        #import app.services.file_service as file_service
        import os
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_chroma import Chroma

        # временно для запуска конвейра
        import importlib

        print("Тип self.user_name")
        print(type(self.user_name))

        if isinstance(self.user_name, str):
            module_name = "pipeline.io_file_operation"
        else:
            module_name = "app.utils.io_file_operation"
        
        io_file_operation = importlib.import_module(module_name)
        # временно для запуска конвейра

        user_folder_path = io_file_operation.return_user_folder(self.user_name)
        print ("gvid_multilingual_e5_large user_folder_path: " + user_folder_path)

        if not os.path.exists(user_folder_path):
            return False
        
        db_folder = os.path.join(user_folder_path, 'db')
        print ("gvid_multilingual_e5_large db_folder: " + db_folder)
        if not os.path.exists(db_folder):
            return False
        
        print ("gvid_multilingual_e5_large start hf_embeddings_model")
        #todo: need parametr for model_kwargs
        hf_embeddings_model = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-large", model_kwargs={"device": "cpu"}) #cuda
        

        print ("gvid_multilingual_e5_large hf_embeddings_model: ")
        vectordb = Chroma(collection_name = "main", 
                          persist_directory=db_folder, 
                          embedding_function=hf_embeddings_model)

        print ("finish gvid_multilingual_e5_large vectordb ")
        return vectordb
    
class gvid_multilingual_e5_large_cosine:
    def __init__(self, user_name):
        self.user_name = user_name
    def get_vectror_db(self):

        print ("start gvid_multilingual_e5_large")
        #import app.services.file_service as file_service
        import os
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_chroma import Chroma

        # временно для запуска конвейра
        import importlib

        print("Тип self.user_name")
        print(type(self.user_name))

        if isinstance(self.user_name, str):
            module_name = "pipeline.io_file_operation"
        else:
            module_name = "app.utils.io_file_operation"
        
        io_file_operation = importlib.import_module(module_name)
        # временно для запуска конвейра

        user_folder_path = io_file_operation.return_user_folder(self.user_name)
        print ("gvid_multilingual_e5_large user_folder_path: " + user_folder_path)

        if not os.path.exists(user_folder_path):
            return False
        
        db_folder = os.path.join(user_folder_path, 'db')
        print ("gvid_multilingual_e5_large db_folder: " + db_folder)
        if not os.path.exists(db_folder):
            return False
        
        print ("gvid_multilingual_e5_large start hf_embeddings_model")
        #todo: need parametr for model_kwargs
        hf_embeddings_model = HuggingFaceEmbeddings(
            model_name="intfloat/multilingual-e5-large", model_kwargs={"device": "cpu"}) #cuda
        

        print ("gvid_multilingual_e5_large hf_embeddings_model: ")
        vectordb = Chroma(collection_name = "main", 
                          persist_directory=db_folder, 
                          embedding_function=hf_embeddings_model,
                          collection_metadata={"hnsw:space": "cosine"})

        print ("finish gvid_multilingual_e5_large vectordb cosine")
        return vectordb