import pytest
from main import app, db, Task


@pytest.fixture
def client():
    # Configurações para o ambiente de teste
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_create_task(client):
    response = client.post('/tasks', json={
        'title': 'Test Task',
        'description': 'This is a test task'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Test Task'
    assert data['description'] == 'This is a test task'


def test_get_tasks(client):
    # Cria uma tarefa primeiro
    client.post('/tasks', json={'title': 'Task 1', 'description': 'Desc 1'})

    response = client.get('/tasks')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]['title'] == 'Task 1'


def test_update_task(client):
    # Cria uma tarefa
    response = client.post('/tasks', json={'title': 'Old Title', 'description': 'Old Desc'})
    task_id = response.get_json()['id']

    # Atualiza a tarefa
    response = client.put(f'/tasks/{task_id}', json={'title': 'New Title', 'description': 'New Desc'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'New Title'
    assert data['description'] == 'New Desc'


def test_delete_task(client):
    # Cria uma tarefa
    response = client.post('/tasks', json={'title': 'Task to Delete'})
    task_id = response.get_json()['id']

    # Deleta a tarefa
    response = client.delete(f'/tasks/{task_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Task deleted'

    # Verifica se foi realmente deletada
    response = client.get('/tasks')
    data = response.get_json()
    assert len(data) == 0
