# имена классов должны начинаться с e_
# и отображать основные характеристики (по усмотрению разработчика)

class e_default:
    def __init__(self):
        print("embeding")
    def get_embeddings(self):
        from langchain.embeddings  import HuggingFaceEmbeddings

        model_name = "cointegrated/LaBSE-en-ru"

        hf_embeddings_model = HuggingFaceEmbeddings(
            #todo: need parametr for model_kwargs
        model_name=model_name, model_kwargs={"device": "cpu"})

        return hf_embeddings_model