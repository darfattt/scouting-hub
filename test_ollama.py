from langchain_ollama import OllamaLLM, OllamaEmbeddings
import time

def test_llm():
    print("Testing Ollama LLM...")
    llm = OllamaLLM(model="deepseek-r1:8b")
    
    start_time = time.time()
    result = llm.invoke("What is the capital of France?")
    end_time = time.time()
    
    print(f"Response time: {end_time - start_time:.2f} seconds")
    print(f"Response: {result}")
    print("LLM test completed successfully!")

def test_embeddings():
    print("\nTesting Ollama Embeddings...")
    embeddings = OllamaEmbeddings(model="deepseek-r1:8b")
    
    start_time = time.time()
    result = embeddings.embed_query("What is the capital of France?")
    end_time = time.time()
    
    print(f"Response time: {end_time - start_time:.2f} seconds")
    print(f"Embedding dimension: {len(result)}")
    print("Embeddings test completed successfully!")

if __name__ == "__main__":
    test_llm()
    test_embeddings()
