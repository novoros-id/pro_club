# имена классов должны начинаться с e_
# и отображать основные характеристики (по усмотрению разработчика)

class e_default:
    def __init__(self):
        print("embeding")
    def get_embeddings(self):
        from langchain_huggingface import HuggingFaceEmbeddings

        model_name = "cointegrated/LaBSE-en-ru"

        hf_embeddings_model = HuggingFaceEmbeddings(
            #todo: need parametr for model_kwargs
        model_name=model_name, model_kwargs={"device": "cpu"})

        return hf_embeddings_model
    
class e_multilingual_e5_large:
    def __init__(self):
        print("embeding")
    def get_embeddings(self):
        print ("start e_multilingual_e5_large")
        from langchain_huggingface import HuggingFaceEmbeddings

        model_name = "intfloat/multilingual-e5-large"

        hf_embeddings_model = HuggingFaceEmbeddings(
            #todo: need parametr for model_kwargs
            model_name=model_name, 
            model_kwargs={"device": "cpu"})

        print ("finish e_multilingual_e5_large")
        return hf_embeddings_model