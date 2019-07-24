import json
from service import app

def test_index():
    request, response = app.test_client.get('/')
    assert response.status == 200
    assert 'text/html' in response.headers.get('content-type')

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

    request, response = app.test_client.post('/api/archives', headers=auth_headers, json={
        "urls" : ["http://www.example.org"],
        "name" : "ArchiveFromTests",
        "headers" : {},
        "forceTor" : False,
    })
    assert response.status == 201
    archive_location = response.headers['location']

    request, response = app.test_client.get(archive_location, headers=auth_headers)
    assert response.status == 200
    assert response.headers.get('content-type') == 'application/json'
    archive_detail = json.loads(response.text)
    assert 'href_download_api' in archive_detail
    assert 'href_detail_api' in archive_detail

    request, response = app.test_client.get(archive_detail['href_download_api'], headers=auth_headers)
    assert response.status == 200
    assert response.headers.get('content-type') == 'application/x-maff'

    request, response = app.test_client.delete(archive_detail['href_detail_api'], headers=auth_headers)
    assert response.status == 204

def test_api_bad_requests():
    auth_headers = {'Authorization': 'Token Z0SbdsCkNXgrvQSGXqZWTsd0ylWVJasO'}
    # missing urls
    request, response = app.test_client.post('/api/archives', headers=auth_headers, json=
        {
            "name" : "ArchiveFromTests",
            "headers" : {},
            "forceTor" : False,
        })
    assert response.status == 400
    assert response.headers.get('content-type') == 'application/json'

    # missing name
    request, response = app.test_client.post('/api/archives', headers=auth_headers, json=
        {
            "urls" : ["http://www.example.org"],
            "headers" : {},
            "forceTor" : False,
        })
    assert response.status == 400
    assert response.headers.get('content-type') == 'application/json'

    # missing headers
    request, response = app.test_client.post('/api/archives', headers=auth_headers, json=
        {
            "urls" : ["http://www.example.org"],
            "name" : "ArchiveFromTests",
            "forceTor" : False,
        })
    assert response.status == 400
    assert response.headers.get('content-type') == 'application/json'

    # json is empty
    request, response = app.test_client.post('/api/archives', headers=auth_headers, json=None)
    assert response.status == 400
    assert response.headers.get('content-type') == 'application/json'

    # json is a list
    request, response = app.test_client.post('/api/archives', headers=auth_headers, json=[])
    assert response.status == 400
    assert response.headers.get('content-type') == 'application/json'

if __name__ == "__main__":
    # index page
    test_index()

    # unauthorized access to archives, post archive and get archive
    test_api_unauth()

    # authorized access
    test_api_auth()

    # bad requests
    test_api_bad_requests()

    print('Tests finished')