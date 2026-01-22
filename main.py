from fastapi import FastAPI, UploadFile, HTTPException, status, File, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response, StreamingResponse, JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from celery.result import AsyncResult
from pdf_processing_worker import pdf_processing, celery_app
from query_worker import query
import uvicorn
import magic
import os
import asyncio

app = FastAPI()

mime = magic.Magic(mime=True)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def form_page(req: Request):
    return templates.TemplateResponse(
        name="landing_page.html",
        context={
            "request": req,
        }
    )

@app.post("/upload", response_class=HTMLResponse)
async def upload_file(req: Request, file: UploadFile = File(...)):
    print(f"File Name: {file.filename}")
    print(f"Content type: {file.content_type}")
    content = await file.read()
    content_type = mime.from_buffer(content)
    if content_type != "application/pdf":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file type. Only pdf file can be uploaded")
    temp_folder = "temp/uploads"
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder, exist_ok=True)
    save_file_path: str = os.path.join(temp_folder, file.filename)
    with open(save_file_path, "wb") as f:
        f.write(content)
    task = pdf_processing.delay(save_file_path)
    print("Task id: ", task.id)
    # query("What is the introduction in the document about?")
    return templates.TemplateResponse(
        name="processing.html",
        context={
            "request": req,
            "file_name": file.filename,
            "content_type": file.content_type,
            "task_id": task.id
        }  
    )

@app.get("/task_status/{task_id}")
def get_status(task_id: str):
    task_result = AsyncResult(task_id, app=celery_app)
    result = {
        "task_id": task_id,    
        "status": task_result.status,
        "result": task_result.result
    }
    print(result)
    return result

@app.get("/chat")
def chat_page(req: Request):
    return templates.TemplateResponse(name="chat.html", context={"request": req})

@app.websocket("/ws/chat")  
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print("Query: ", data)  
            # reponse_text = await query(data)     
            # await websocket.send_text(reponse_text) 
            async for chunk in query(data):
                await websocket.send_text(chunk)
            await websocket.send_text("[DONE]")    

    except WebSocketDisconnect:
        print("Client Disconnected")




if __name__=="__main__":
    uvicorn.run("main:app", reload=True)
 
