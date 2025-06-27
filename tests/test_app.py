import pytest
import os
import shutil
from app import app # 

@pytest.fixture
def client():
    # 
    test_news_dir = 'test_news'
    if os.path.exists(test_news_dir):
        shutil.rmtree(test_news_dir)
    os.makedirs(test_news_dir)

    # 
    original_news_path = app.config.get('NEWS_DIR', 'news')
    app.config['NEWS_DIR'] = test_news_dir # 

    app.testing = True
    with app.test_client() as client:
        yield client

    # 
    shutil.rmtree(test_news_dir)
    # 
    app.config['NEWS_DIR'] = original_news_path

def test_index_page(client):
    # 
    with open('test_news/20230101.md', 'w') as f:
        f.write('# Test Markdown News 1')
    with open('test_news/20230102.html', 'w') as f:
        f.write('<!DOCTYPE html><html><head><title>Test HTML News 2</title></head><body></body></html>')

    rv = client.get('/')
    assert rv.status_code == 200
    assert b'Test Markdown News 1' in rv.data
    assert b'Test HTML News 2' in rv.data

def test_show_md_news(client):
    with open('test_news/test_md.md', 'w') as f:
        f.write('# Hello Markdown\n\nThis is a test.')
    
    rv = client.get('/test_md')
    assert rv.status_code == 200
    assert b'<h1>Hello Markdown</h1>' in rv.data
    assert b'<p>This is a test.</p>' in rv.data

def test_show_html_news(client):
    with open('test_news/test_html.html', 'w') as f:
        f.write('<!DOCTYPE html><html><head><title>HTML Test</title></head><body><h1>HTML Content</h1></body></html>')
    
    rv = client.get('/test_html')
    assert rv.status_code == 200
    assert b'<h1>HTML Content</h1>' in rv.data
    assert b'<title>HTML Test</title>' in rv.data

def test_show_nonexistent_news(client):
    rv = client.get('/nonexistent_news')
    assert rv.status_code == 404
    assert b'404 - \xe6\x96\xb0\xe9\x97\xbb\xe6\x9c\xaa\xe6\x89\xbe\xe5\x88\xb0' in rv.data # "

# 
def login(client, username, password):
    return client.post('/login', data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_save_new_md_file(client):
    login(client, os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD'))
    rv = client.post('/api/save', json={
        'filename': 'new_md_file',
        'content': '# New MD Content',
        'file_type': 'md'
    })
    assert rv.status_code == 200
    assert os.path.exists('test_news/new_md_file.md')
    with open('test_news/new_md_file.md', 'r') as f:
        assert f.read() == '# New MD Content'

def test_save_new_html_file(client):
    login(client, os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD'))
    rv = client.post('/api/save', json={
        'filename': 'new_html_file',
        'content': '<html><body>New HTML Content</body></html>',
        'file_type': 'html'
    })
    assert rv.status_code == 200
    assert os.path.exists('test_news/new_html_file.html')
    with open('test_news/new_html_file.html', 'r') as f:
        assert f.read() == '<html><body>New HTML Content</body></html>'

def test_edit_existing_file(client):
    with open('test_news/edit_me.md', 'w') as f:
        f.write('# Original Content')
    
    login(client, os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD'))
    rv = client.post('/api/save', json={
        'filename': 'edit_me',
        'content': '# Updated Content',
        'original_filename': 'edit_me',
        'file_type': 'md'
    })
    assert rv.status_code == 200
    assert os.path.exists('test_news/edit_me.md')
    with open('test_news/edit_me.md', 'r') as f:
        assert f.read() == '# Updated Content'

def test_rename_file(client):
    with open('test_news/old_name.md', 'w') as f:
        f.write('# Old Content')
    
    login(client, os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD'))
    rv = client.post('/api/save', json={
        'filename': 'new_name',
        'content': '# Old Content',
        'original_filename': 'old_name',
        'file_type': 'md'
    })
    assert rv.status_code == 200
    assert not os.path.exists('test_news/old_name.md')
    assert os.path.exists('test_news/new_name.md')

def test_save_filename_conflict(client):
    with open('test_news/conflict.md', 'w') as f:
        f.write('Existing content')
    
    login(client, os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD'))
    rv = client.post('/api/save', json={
        'filename': 'conflict',
        'content': 'New content',
        'file_type': 'md'
    })
    assert rv.status_code == 400 # Should return error for conflict

def test_delete_md_file(client):
    with open('test_news/delete_me.md', 'w') as f:
        f.write('Content to delete')
    
    login(client, os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD'))
    rv = client.post('/api/delete/delete_me')
    assert rv.status_code == 200
    assert not os.path.exists('test_news/delete_me.md')

def test_delete_html_file(client):
    with open('test_news/delete_me.html', 'w') as f:
        f.write('Content to delete')
    
    login(client, os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD'))
    rv = client.post('/api/delete/delete_me')
    assert rv.status_code == 200
    assert not os.path.exists('test_news/delete_me.html')

def test_delete_nonexistent_file(client):
    login(client, os.getenv('ADMIN_USERNAME'), os.getenv('ADMIN_PASSWORD'))
    rv = client.post('/api/delete/nonexistent_file')
    assert rv.status_code == 404
