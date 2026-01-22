Here is a professional and concise `README.md` for your GitHub repository.

---

# DocQuery AI 📄🤖

**DocQuery AI** is a locally hosted, Retrieval-Augmented Generation (RAG) application that enables users to upload PDF documents and engage in context-aware conversations.

By leveraging **Ollama (Llama 3.1)** for local inference and a robust **Celery + Redis** backend for asynchronous processing, the application ensures high performance without compromising user privacy.

## 🏗 System Architecture

The project implements a hybrid architecture to handle resource-intensive tasks and real-time interaction efficiently:

1. **Ingestion Pipeline (Asynchronous):**
* **Upload:** Users upload PDFs via FastAPI.
* **Queue:** The server offloads the heavy processing task to **Celery** via **Redis**.
* **Feedback:** The frontend uses **Polling** (every 2s) to check task status via Redis, ensuring the UI remains responsive during ingestion.
* **Vectorization:** A dedicated worker utilizes `PyPDFLoader` and `RecursiveCharacterTextSplitter`. Chunks are hashed and checked against **ChromaDB** to ensure **only new, unique chunks** are embedded and stored.


2. **Inference Engine (Real-time):**
* **Communication:** A **WebSocket** connection is established for the chat interface to allow bidirectional, low-latency communication.
* **Retrieval:** User queries trigger a similarity search in ChromaDB (Top-k=3).
* **Generation:** Context and query are sent to **Ollama (Llama 3.1)**.
* **Streaming:** Responses are yielded as Python generator objects and streamed word-by-word to the frontend, providing an instant "typewriter" experience.



## 🚀 Key Features

* **Local RAG Implementation:** fast and private document analysis using local LLMs.
* **Smart Ingestion:** Efficient text splitting and deduplication logic prevents redundant data in the vector store.
* **Background Processing:** Heavy PDF parsing runs on a Celery worker, preventing server blocking.
* **Real-time Streaming:** WebSockets enable token-by-token response generation.
* **Interactive UI:** Clean HTML/TailwindCSS interface with live processing status and chat history.

## 🛠 Tech Stack

* **Backend:** FastAPI, Python 3.x
* **Task Queue:** Celery, Redis
* **AI & LLM:** Ollama (Llama 3.1), LangChain
* **Vector Store:** ChromaDB
* **Embeddings:** HuggingFace (`sentence-transformers/all-MiniLM-L6-v2`)
* **Frontend:** HTML5, JavaScript, TailwindCSS

## 📦 Installation & Setup

**Prerequisites:**

* Python 3.10+
* [Redis](https://redis.io/) (Running locally or via Docker)
* [Ollama](https://ollama.com/) (With `llama3.1` model pulled)

**1. Clone the repository**

```bash
git clone https://github.com/yourusername/docquery_ai.git
cd docquery_ai

```

**2. Install dependencies**

```bash
pip install -r requirements.txt

```

**3. Start the Services**
You need three separate terminal windows:

* **Terminal 1 (Redis):** Ensure Redis is running (use the official redis Docker image).
```bash
docker run -p 6379:6379 -d redis

```


* **Terminal 2 (Celery Worker):**
```bash
# Windows users add: -P solo
celery -A pdf_processing_worker.celery_app worker --loglevel=info -P solo

```


* **Terminal 3 (FastAPI Server):**
```bash
python main.py

```


**4. Access the App**
Open your browser and navigate to `http://localhost:8000`.

## 📄 License

This project is licensed under the MIT License.
