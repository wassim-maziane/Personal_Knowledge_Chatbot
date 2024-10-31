from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.1:8b")
print(llm.invoke("Hi AI!"))
