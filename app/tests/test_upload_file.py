import pytest


from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_player_log(player_log):
    response = client.post("/uploadfile/", files={"file": open(player_log, "rb")})
    #TODO do more intense testing things :)
