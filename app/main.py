from fastapi import FastAPI, File, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import uvicorn


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


def parse_database():
    database_link = "https://raw.githubusercontent.com/Manuel-777/MTG-Arena-Tool/master/src/resources/database.json"
    response = requests.get(database_link)
    return response.json()['cards']


db = parse_database()


@app.get("/")
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/items/{id}")
async def read_item(request: Request, id: str):
    return templates.TemplateResponse("item.html", {"request": request, "id": id})


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    for line in file.read():
        print(line)
    return {"filename": file.filename}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info", reload=True)
