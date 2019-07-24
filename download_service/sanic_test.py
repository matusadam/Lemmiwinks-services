import json
from service import app

def test_index():
    request, response = app.test_client.get('/')
    assert response.status == 200
    assert 'text/html' in response.headers.get('content-type')

def test_api():
    request, response = app.test_client.post('/api/download', json=
        {
            "resourceURL" : "http://www.example.org",
            "headers" : {},
            "useTor" : False,
        })
    assert response.status == 200
    assert response.headers.get('content-type') == 'application/json'

    # test headers
    request, response = app.test_client.post('/api/download', json=
        {
            "resourceURL" : "http://www.example.org",
            "headers" : {'Accept-Language': 'de'},
            "useTor" : False,
        })
    assert response.status == 200
    assert response.headers.get('content-type') == 'application/json'

    # test Tor for download
    request, response = app.test_client.post('/api/download', json=
        {
            "resourceURL" : "http://www.example.org",
            "headers" : {},
            "useTor" : True,
        })
    assert response.status == 200
    assert response.headers.get('content-type') == 'application/json'


def test_api_bad_requests():

    # missing resourceURL
    request, response = app.test_client.post('/api/download', json=
        {
            "headers" : {},
            "useTor" : True
        })
    assert response.status == 400
    assert response.headers.get('content-type') == 'application/json'

    # missing headers
    request, response = app.test_client.post('/api/download', json=
        {
            "resourceURL" : "http://www.example.org",
            "useTor" : True,
        })
    assert response.status == 400
    assert response.headers.get('content-type') == 'application/json'

    # missing useTor
    request, response = app.test_client.post('/api/download', json=
        {
            "resourceURL" : "http://www.example.org",
            "headers" : {},
        })
    assert response.status == 400
    assert response.headers.get('content-type') == 'application/json'

    # json is empty
    request, response = app.test_client.post('/api/download', json=None)
    assert response.status == 400
    assert response.headers.get('content-type') == 'application/json'

    # json is a list
    request, response = app.test_client.post('/api/download', json=[])
    assert response.status == 400
    assert response.headers.get('content-type') == 'application/json'
    

if __name__ == "__main__":
    # index page
    test_index()
    test_api()
    test_api_bad_requests()
    print('Tests finished')