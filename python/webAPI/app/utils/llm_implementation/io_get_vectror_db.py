# имена классов должны начинаться с gvid_
# и отображать основные характеристики (по усмотрению разработчика)

class gvid_default:
    def __init__(self, user_name):
        self.user_name = user_name
    def get_vectror_db(self):

        import app.services.file_service as file_service
        import os
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_chroma import Chroma
        from app.services.file_service import return_user_folder

        user_folder_path = return_user_folder(self.user_name)
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
