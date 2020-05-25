import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile
import json
from collections import defaultdict

from fastapi import FastAPI, File, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import requests
import uvicorn


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

WILDCARD_KEYS = ["wcCommonDelta", "wcUncommonDelta", "wcRareDelta", "wcMythicDelta"]


def parse_database():
    database_link = "https://raw.githubusercontent.com/Manuel-777/MTG-Arena-Tool/master/src/resources/database.json"
    response = requests.get(database_link)
    return response.json()['cards']


db = parse_database()


def save_upload_file_tmp(upload_file: UploadFile) -> Path:
    try:
        suffix = Path(upload_file.filename).suffix
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = Path(tmp.name)
    finally:
        upload_file.file.close()
    return tmp_path


@app.get("/")
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


def generate_updates(file):
    with open(file, "r") as inf:
        for line in inf:
            try:
                if "Inventory.Updated " in line:
                    results = line.rstrip().split("Inventory.Updated ")[1]
                    js = json.loads(results)
                    payload = js["payload"]
                    updates = payload["updates"]
                    for update in updates:
                            delta = update["delta"]
                            cards_added = delta["cardsAdded"]
                            wildcards_dict = {}
                            for wildcard in WILDCARD_KEYS:
                                wildcards_dict[wildcard] = delta[wildcard]
                            yield cards_added, wildcards_dict
            except Exception as e:
                continue


@app.post("/uploadfile/")
async def create_upload_file(request: Request, file: UploadFile = File(...)):
    c_card_ids = defaultdict(int)
    c_wild_cards = defaultdict(int)
    try:
        tmp_path = save_upload_file_tmp(file)
        for result in generate_updates(tmp_path):
            for card_id in result[0]:
                if str(card_id) in db:
                    c_card_ids[db[str(card_id)]["name"]] += 1
            for k, v in result[1].items():
                k = k.replace("wc", "").replace("Delta", "")
                c_wild_cards[k] += v
    finally:
        tmp_path.unlink()  # Delete the temp file

    return templates.TemplateResponse("deck.html", {"request": request, "c_card_ids": c_card_ids, "c_wild_cards": c_wild_cards})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, log_level="info", reload=True)
