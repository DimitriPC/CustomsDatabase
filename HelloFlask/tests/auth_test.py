import pytest
from HelloFlask.models import *

# code 200: render_template code 302: redirect

def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_login_succesful(client, test_user):
    response = client.post("/login", data={
        "name": "validName",
        "password": "validPassword"
    })

    assert response.status_code == 302
    assert "/matches" in response.headers["Location"]


def test_username_not_found(client):
    response = client.post("/login", data={
        "name": "invalidName",
        "password": "validPassword"
    })

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_password_wrong(client, test_user):
    response = client.post("/login", data={
        "name": "validName",
        "password": "invalidPassword"
    })

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_empty_name(client):
    response = client.post("/login", data={
        "name": "",
        "password": "validPassword"
    })

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_empty_password(client, test_user):
    response = client.post("/login", data={
        "name": "validName",
        "password": ""
    })

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_special_chars_name(client):
    response = client.post("/login", data={
        "name": "@👌",
        "password": "validPassword"
    })

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_special_chars_password(client, test_user):
    response = client.post("/login", data={
        "name": "validName",
        "password": "👌"
    })

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]