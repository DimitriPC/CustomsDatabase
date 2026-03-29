import pytest
import bcrypt

from HelloFlask import create_app, TestConfig, db
from HelloFlask.models import User


# -------------------------
# App fixture
# -------------------------
@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


# -------------------------
# Client fixture
# -------------------------
@pytest.fixture
def client(app):
    return app.test_client()


# -------------------------
# Database session (isolated per test)
# -------------------------
@pytest.fixture
def db_session(app):
    connection = db.engine.connect()
    transaction = connection.begin()

    db.session.bind = connection

    yield db.session

    transaction.rollback()
    db.session.remove()
    connection.close()


# -------------------------
# Test user fixture
# -------------------------
@pytest.fixture
def test_user(db_session):
    hashed_pw = bcrypt.hashpw(
        "validPassword".encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    user = User(
        real_name="validName",
        username="validUsername",
        password=hashed_pw,
        is_admin=False
    )

    db_session.add(user)
    db_session.commit()

    return user


# -------------------------
# Logged-in client (optional)
# -------------------------
@pytest.fixture
def logged_in_client(client, test_user):
    client.post("/login", data={
        "name": "validName",
        "password": "validPassword"
    })
    return client

