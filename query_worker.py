from embedding_func import get_embedding_function
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
import time


CHROMA_PATH = "chroma"
PROMPT_TEMPLATE = '''
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
'''


async def query(query_text: str):
    embedding_function = get_embedding_function()
    vector_store = Chroma(
        collection_name="pdf_chunks", embedding_function=embedding_function, persist_directory=CHROMA_PATH
    )
    results = vector_store.similarity_search_with_score(query_text, k=3)
    print("Number of sources - ", len(results))
    if len(results):
        print(type(results[0][0]))
    sources = [doc.metadata.get("id") for doc, score in results]
    sources_text = ", ".join(sources)
    context_text = "\n\n---\n\n".join([doc.page_content for doc, score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    model = ChatOllama(
        model="llama3.1",
        temperature=0.7
    )
    message = [
        ("system", "You are an educational assistant, you will answer questions based on the document uploaded"),
        ("human", prompt)
    ]
    start_time = time.time()
    async for chunk in model.astream(message):
        yield chunk.content
    end_time = time.time()
    duration = end_time - start_time
    print(f"Time taken for generating response: {duration} seconds")
    if sources_text:
        yield f"[SOURCES]: {sources_text}"
    if duration:
        yield f"[RESPONSE DURATION]: {duration} seconds"



    

