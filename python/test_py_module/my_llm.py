from langchain_ollama import OllamaLLM

llm = OllamaLLM(
    model="llama3", temperature = "0.1"
)

def llm_invoke (request):
    return llm.invoke(request)