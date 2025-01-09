# имена классов должны начинаться с promt_
# и отображать основные характеристики (по усмотрению разработчика)

class promt_default:
    def __init__(self, data, prompt):
        self.data = data
        self.prompt = prompt
    def get_promt(self):
        return f"Вы полезный ассистент. Вы отвечаете на вопросы о документации, используя эти данные: {self.data}. Ответь на русском языке на этот запрос: {self.prompt} и укажи source "
    
class promt_test:
    def __init__(self, data, prompt):
        self.data = data
        self.prompt = prompt
    def get_promt(self):
        return f"DOCUMENT: {self.data} QUESTION: {self.prompt} INSTRUCTIONS: Answer the users QUESTION using the DOCUMENT text above. Keep your answer ground in the facts of the DOCUMENT. If the DOCUMENT doesnt contain the facts to answer the QUESTION return НЕТОТВЕТА. Ответь на русском языке "