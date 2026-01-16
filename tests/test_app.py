import pytest
from app import app, db, Todo

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_home_redirect(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Login' in response.data

def test_add_todo(client):
    with app.app_context():
        todo = Todo(task='Test Task', done=False, user_id='123')
        db.session.add(todo)
        db.session.commit()
        assert Todo.query.count() == 1
