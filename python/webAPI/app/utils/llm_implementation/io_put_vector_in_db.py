# имена классов должны начинаться с pvid_
# и отображать основные характеристики (по усмотрению разработчика)

class pvid_default:
    def __init__(self, separate_text, embedding, user_name):
        self.separate_text = separate_text
        self.embedding = embedding
        self.user_name = user_name
    def put_vector_in_db(self):

        import io_file_operation
        import os
        from langchain_chroma import Chroma

        user_folder_path = io_file_operation.return_user_folder(self.user_name)
        if not os.path.exists(user_folder_path):
            return False
        
        db_folder = os.path.join(user_folder_path, 'db')

        if not os.path.exists(db_folder):
            return False

        vector_db = Chroma.from_documents(
            collection_name = "main",
            documents=self.separate_text,
            embedding=self.embedding,
            persist_directory=db_folder,
            )
        
        return True