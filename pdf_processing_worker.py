import os
import time
from celery import Celery
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from embedding_func import get_embedding_function

CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CHROMA_PATH = "chroma"

celery_app = Celery("pdf_processing", broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)

@celery_app.task(name="pdf_processing")
def pdf_processing(file_path: str):
    '''
    Docstring for pdf_processing
    Celery task to handle pdf processing
    '''
    print(f"Worker received file for processing: {file_path}")
    loader = PyPDFLoader(file_path)
    docs = loader.load()     # Loading pdf docs is a list of pages in pdf each page is a langchain document object
    print(f"Number of pages in pdf: {len(docs)}")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
    )
    chunks = text_splitter.split_documents(docs) # Splitting each page into chunks
    print(f"Number of chunks splitted: {len(chunks)}")
    # Creating/loading database
    vector_store = Chroma(
        collection_name="pdf_chunks", embedding_function=get_embedding_function(), persist_directory=CHROMA_PATH
    )
    # print(vector_store)
    # Adding ids to each chunk
    chunks_with_ids = calculate_chunk_ids(chunks)
    print(f"👉 Number of documents in pdf file: {len(chunks_with_ids)}")
    # Add or update the documents
    existing_items = vector_store.get(include=[])
    # print(existing_items)
    existing_ids = set(existing_items["ids"])
    print(f"👉 Number of existing documents in vector store: {len(existing_ids)}")
    # Only add documents that do not exist in vector store
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    
    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        vector_store.add_documents(documents=new_chunks, ids=new_chunk_ids)
    else:
        print("👉 No documents to add") 

    return {"status": "completed", "message": "PDF splitted and embedded successfully!"}    


def calculate_chunk_ids(chunks: list):
    # Creating IDs for chunks: Page Source: Page Number: Chunk Index
    last_page_id = None
    current_chunk_idx = 0

    for chunk in chunks:
        # get the source and page_num for current chunk
        source = chunk.metadata.get("source")
        page_num = chunk.metadata.get("page")
        current_page_id = f"{source}: {page_num}"
        # check if current page is same as lastpage, new page the chunk idx resets
        if current_page_id==last_page_id:
            current_chunk_idx+=1
        else:
            current_chunk_idx=0
        
        chunk_id = f"{current_page_id}: {current_chunk_idx}"
        last_page_id=current_page_id

        chunk.metadata["id"] = chunk_id
    return chunks

# def temp_pdf_processing(file_path: str):

  








