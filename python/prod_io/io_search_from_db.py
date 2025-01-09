# имена классов должны начинаться с s_
# и отображать основные характеристики (по усмотрению разработчика)

class s_default:
    def __init__(self, prompt, user_name, vectordb):
        self.prompt = prompt
        self.user_name = user_name
        self.vectordb = vectordb
    def seach_from_db(self):
        return self.vectordb.similarity_search(self.prompt,k=4)