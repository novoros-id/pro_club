# имена классов должны начинаться с pvid_
# и отображать основные характеристики (по усмотрению разработчика)

class pvid_default:
    def __init__(self, separate_text, embedding, user_name):
        self.separate_text = separate_text
        self.embedding = embedding
        self.user_name = user_name
    def put_vector_in_db(self):

        print ("Start pvid_default")
        import os
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

        print ("pvid_default user_folder_path:" + user_folder_path)
        if not os.path.exists(user_folder_path):
            return False
        
        db_folder = os.path.join(user_folder_path, 'db')
        print ("pvid_default db_folder" + db_folder)
        if not os.path.exists(db_folder):
            return False

        print ("pvid_default starting from_documents")
        vector_db = Chroma.from_documents(
            collection_name = "main",
            documents=self.separate_text,
            embedding=self.embedding,
            persist_directory=db_folder,
            )
        
        print ("finish pvid_default")

        return True