import json
from service import app

def test_index():
    request, response = app.test_client.get('/')
    assert response.status == 200

def test_api_unauth():
    data = {
        "urls" : ["http://www.example.org"],
        "name" : "ArchiveFromTests",
        "headers" : {},
        "forceTor" : False,
    }
    request, response = app.test_client.get('/api/archives')
    assert response.status == 401
    request, response = app.test_client.post('/api/archives', json=data)
    assert response.status == 401
    request, response = app.test_client.get('/api/archives/badid')
    assert response.status == 401
    request, response = app.test_client.get('/api/archives/badid/bad.maff')
    assert response.status == 401

def test_api_auth():
    # auth header
    auth_headers = {'Authorization': 'Token Z0SbdsCkNXgrvQSGXqZWTsd0ylWVJasO'}
    data = {
        "urls" : ["http://www.example.org"],
        "name" : "ArchiveFromTests",
        "headers" : {},
        "forceTor" : False,
    }
    request, response = app.test_client.get('/api/archives', headers=auth_headers)
    assert response.status == 200
    assert response.headers.get('content-type') == 'application/json'

    request, response = app.test_client.post('/api/archives', json=data, headers=auth_headers)
    assert response.status == 201
    archive_location = response.headers['location']

    request, response = app.test_client.get(archive_location, headers=auth_headers)
    assert response.status == 200
    assert response.headers.get('content-type') == 'application/json'
    archive_detail = json.loads(response.text)
    assert 'href_download_api' in archive_detail

    request, response = app.test_client.get(archive_detail['href_download_api'], headers=auth_headers)
    assert response.status == 200
    assert response.headers.get('content-type') == 'application/x-maff'

if __name__ == "__main__":
    # index page
    test_index()

    # unauthorized access to archives, post archive and get archive
    test_api_unauth()

    # authorized access
    test_api_auth()

    print('Archive service tests finished')