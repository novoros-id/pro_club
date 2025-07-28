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

class s_k_150:
    def __init__(self, prompt, user_name, vectordb):
        self.prompt = prompt
        self.user_name = user_name
        self.vectordb = vectordb
    def seach_from_db(self):
        print ("start s_k_150")
        threshold = 0.4  # максимальное расстояние (чем меньше — тем строже)
        results = self.vectordb.similarity_search_with_score(self.prompt, k=150)
        filtered_docs = []

        for doc, score in results:
            if score <= threshold:  # score = расстояние
                #print(doc.metadata)
                filtered_docs.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                })
        print(f"filtered_docs: {len(filtered_docs)}")
        return filtered_docs