# имена классов должны начинаться с s_
# и отображать основные характеристики (по усмотрению разработчика)

class s_default:
    def __init__(self, prompt, user_name, vectordb):
        self.prompt = prompt
        self.user_name = user_name
        self.vectordb = vectordb
    def seach_from_db(self):
        return self.vectordb.similarity_search(self.prompt,k=4)

class s_k_five:
    def __init__(self, prompt, user_name, vectordb):
        self.prompt = prompt
        self.user_name = user_name
        self.vectordb = vectordb
    def seach_from_db(self):
        return self.vectordb.similarity_search(self.prompt,k=5)
    
class s_k_2:
    def __init__(self, prompt, user_name, vectordb):
        self.prompt = prompt
        self.user_name = user_name
        self.vectordb = vectordb
    def seach_from_db(self):
        print ("start s_k_2")
        return self.vectordb.similarity_search(self.prompt,k=2)