import os, re
from datetime import datetime
import argparse
from functools import wraps
import base64

from sanic import Sanic
from sanic import response
from sanic_auth import Auth, User
from sanic_token_auth import SanicTokenAuth
from tinydb import TinyDB, Query

from schema import ArchivePostSchema
from name_generator import ArchiveName
from lemmiwinks_top import ArchiveServiceLemmiwinks
from utilities import Archives

# Sanic init
app = Sanic()

# Sanic-auth
app.config.AUTH_LOGIN_ENDPOINT = 'login'
auth = Auth(app)

session = {}
@app.middleware('request')
async def add_session(request):
    request['session'] = session

db = TinyDB('db/login_access')

# API auth
def api_auth_required():
    def decorator(f):
        @wraps(f)
        async def privileged(request, *args, **kwargs):
            # Authorization Basic
            if request.token == None:
                # no auth header
                return response.json(None, 401)

            try:
                print(request.token)
                _, auth_token = request.token.split(' ')
                decoded = base64.b64decode(auth_token).decode("utf-8")
                username, password = decoded.split(":")
            except Exception:
                # bad token
                return response.json(None, 401)

            q = Query()
            result = next(iter(
                db.search((q.username == username) & (q.password == password))
            ), None)
            if result:
                # the user is authorized.
                return await f(request, *args, **kwargs)
            else:
                # incorrect user
                return response.json(None, 401)
        return privileged
    return decorator

# Sanic routes
@app.route('/', methods=['GET'])
async def get_index(request):
    """get_index

    Main page containing basic information and navigation.

    :rtype: str
    """
    with open("www/index.html", "r", encoding='utf-8') as f:
        index = f.read()
    with open("www/style.css", "r", encoding='utf-8') as f:
        style = f.read()

    if auth.current_user(request):
        with open("www/index_user.html", "r", encoding='utf-8') as f:
            index_user = f.read()
        return response.html(index.format(style, index_user))
    else:
        # show login to guest
        with open("www/index_guest.html", "r", encoding='utf-8') as f:
            index_guest = f.read()
        return response.html(index.format(style, index_guest))


@app.route('/login', methods=['GET'])
async def login(request):
    """Login HTML page

    Login page with login form.
    """
    with open("www/style.css", "r", encoding='utf-8') as f:
        style = f.read()
    if auth.current_user(request):
        return response.redirect('/')
    else:
        with open("www/login.html", "r", encoding='utf-8') as f:
            login = f.read()
        return response.html(login.format(style, ''))

@app.route('/login', methods=['POST'])
async def login(request):
    """Authenticate a user

    Checks and authenticates a user and saves into session. 
    Redirects to the main page on corrent login,
    else displays error message.
    """

    username = request.form.get('username')
    password = request.form.get('password')

    with open("www/login.html", "r", encoding='utf-8') as f:
        login = f.read()
    with open("www/style.css", "r", encoding='utf-8') as f:
        style = f.read()

    q = Query()
    result = next(iter(
        db.search((q.username == username) & (q.password == password))
        ), None)
    if result:
        user = User(id=result.get('id'),name=username)
        auth.login_user(request, user)
        return response.redirect('/')
    else:
        msg_bad_login = '<b style="color:red;">Incorrect username or password</b>'
        return response.html(login.format(style, msg_bad_login))

@app.route('/logout', methods=['GET'])
@auth.login_required
async def logout(request):
    """Logout current user

    Logout user in this session and redirect to main page.
    """

    auth.logout_user(request)
    return response.redirect('/')

@app.route('/archives', methods=['GET'])
@auth.login_required
async def get_archives(request):
    """Archives collection.

    Gets HTML page with a list of all archives and a POST form for creating
    a new archive from given URL and options.

    :rtype: str
    """

    with open("www/archives.html", "r", encoding='utf-8') as f:
        html = f.read()
    with open("www/style.css", "r", encoding='utf-8') as f:
        style = f.read()

    msg = ''
    html_archive_list = ''
    archives = Archives()
    for detail in archives.details():
        html_archive_list += '<tr><th><a href="{}">{}</a></th><th>{}</th><th>{}</th><th>{}</th></tr>'.format(
            detail['href_detail'], detail['name'], detail['aid'], detail['ctime'], detail['size']
        )

    return response.html(html.format(style, html_archive_list, msg))

@app.route('/archives', methods=['POST'])
@auth.login_required
async def post_archives(request):
    """Posts form data for a new archive creation

    A new archive will be created from given URLs. The view will
    be updated with a status message.

    :rtype: str
    """
    print(request.form.get('forceTor'))
    if request.form.get('forceTor'):
        _forceTor = True
    else:
        _forceTor = False

    archive_data = {
        "urls" : [ request.form.get('url') ],
        "name" : request.form.get('name'),
        "forceTor" : _forceTor,
        "headers" : {}
    }
    if ArchivePostSchema(archive_data).is_valid():
        archive_name = ArchiveName(name=archive_data['name'], urls=archive_data['urls'])
        if 'args' in globals():
            aio_archive = ArchiveServiceLemmiwinks(archive_data=archive_data, 
                archive_name=archive_name.full_name,
                download_service_url=args.download_service_url)
        else:
            aio_archive = ArchiveServiceLemmiwinks(archive_data=archive_data, 
                archive_name=archive_name.full_name,
                download_service_url='http://0.0.0.0:8081')
        await aio_archive.task_executor()
        msg = '<b style="color:green;">Archive {} created.</b>'.format(archive_name)
        status = 201
    else:
        msg = '<b style="color:red;">Incorrect form request.</b>'
        status = 400

    with open("www/archives.html", "r", encoding='utf-8') as f:
        html = f.read()
    with open("www/style.css", "r", encoding='utf-8') as f:
        style = f.read()

    html_archive_list = ''
    archives = Archives()
    for detail in archives.details():
        html_archive_list += '<tr><th><a href="{}">{}</a></th><th>{}</th><th>{}</th><th>{}</th></tr>'.format(
            detail['href_detail'], detail['name'], detail['aid'], detail['ctime'], detail['size']
        )

    return response.html(html.format(style, html_archive_list, msg), status=status)


@app.route('/archives/<id>', methods=['GET'])
@auth.login_required
async def get_archive_item(request, id):
    """Archive item details

    Gets HTML page with archive given by its ID. Contains file download link.

    :param id: 
    :type id: int

    :rtype: str
    """
    with open("www/style.css", "r", encoding='utf-8') as f:
        style = f.read()
    archives = Archives()
    detail = archives.searchById(id)
    if detail:
        with open("www/archiveDetail.html", "r", encoding='utf-8') as f:
            html = f.read()
        html = html.format(style, detail['name'], detail['file'], detail['aid'], detail['ctime'], detail['size'], detail['href_download'])
        return response.html(html)
    else:
        with open("www/notfound.html", "r", encoding='utf-8') as f:
            html = f.read()
        html = html.format(id)
        return response.html(html, status=404)

    
@app.route('/archives/<id>/<filename>', methods=['GET'])
@auth.login_required
async def get_archive_file(request, id, filename):
    """Downloads the archive

    Downloads the archive given by its ID. 

    :param id: 
    :type id: int
    :param filename: 
    :type filename: string

    :rtype: str
    """

    archives = Archives()
    detail = archives.searchById(id)
    if detail and detail['file'] == filename:
        return await response.file_stream(filename, headers={"Content-Type" : "application/x-maff"})
    else:
        with open("www/notfound.html", "r", encoding='utf-8') as f:
            html = f.read()   
        return response.html(html.format(filename), status=404)


# API routes

@app.route('/api/archives', methods=['GET'])
@api_auth_required()
async def api_get_archives(request):
    """Archives collection.

    Gets JSON collection of all archives. Use query params.

    :rtype: json
    """

    archives = Archives()
    # query string parse
    try:
        search_name = request.args['name'][0]
    except KeyError:
        search_name = ''
    try:
        skip = int(request.args['skip'][0])
    except KeyError:
        skip = 0
    try:
        limit = int(request.args['limit'][0])
    except KeyError:
        limit = 50

    details = archives.searchByName(search_name)
    details = details[skip:skip+limit]

    return response.json(details)

@app.route('/api/archives', methods=['POST'])
@api_auth_required()
async def api_post_archives(request):
    """Posts data for new archive creation

    A new archive will be created from given URLs. On success
    the archive reference will be in the location response header.

    :rtype: json
    """
    if ArchivePostSchema(request.json).is_valid():
        archive_data = {
            "urls" : request.json.get('urls'),
            "name" : request.json.get('name'),
            "forceTor" : request.json.get('forceTor'),
            "headers" : request.json.get('headers')
        }
        archive_name = ArchiveName(name=archive_data['name'], urls=archive_data['urls'])

        if 'args' in globals():
            aio_archive = ArchiveServiceLemmiwinks(archive_data=archive_data, 
                archive_name=archive_name.full_name,
                download_service_url=args.download_service_url)
        else:
            aio_archive = ArchiveServiceLemmiwinks(archive_data=archive_data, 
                archive_name=archive_name.full_name,
                download_service_url='http://0.0.0.0:8081')

        try:
            await aio_archive.task_executor()
        except Exception as e:
            # something went wrong, archive not created
            print(e)
            return response.json(None, status=204)
        else:
            return response.json(None, status=201, headers={'Location': archive_name.href_detail_api})
    else:
        # bad request
        return response.json(None, status=400)
        
@app.route('/api/archives/<id>', methods=['GET'])
@api_auth_required()
async def api_get_archive_item(request, id):
    """Gets archive item details

    Gets JSON representation of archive item given by id.

    :param id: 
    :type id: int

    :rtype: json
    """

    archives = Archives()
    detail = archives.searchById(id)
    if detail:
        return response.json(detail)
    else:
        return response.json(None, status=404)

@app.route('/api/archives/<id>', methods=['DELETE'])
@api_auth_required()
async def api_delete_archive_item(request, id):
    """Deletes the archive

    Deletes the archive given by its ID. 

    :param id: 
    :type id: int

    :rtype: str
    """

    archives = Archives()
    detail = archives.searchById(id)
    if detail:
        os.remove(detail['file'])
    return response.json(None, status=204)

@app.route('/api/archives/<id>/<filename>', methods=['GET'])
@api_auth_required()
async def api_get_archive_file(request, id, filename):
    """Downloads the archive

    Downloads the archive file given by its ID and filename. 

    :param id: 
    :type id: int
    :param filename: 
    :type filename: string

    :rtype: str
    """

    archives = Archives()
    detail = archives.searchById(id)
    if detail and detail['file'] == filename:
        return await response.file_stream(filename, headers={"Content-Type" : "application/x-maff"})
    else:
        return response.json(None, status=404)


# parse command line arguments and run Sanic server
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Start the archive service')
    parser.add_argument('--download_service_url', type=str, default='http://0.0.0.0:8081',
                    help='Download service URL to be used by this service')
    args = parser.parse_args()

    app.run(host="0.0.0.0", port="8080")


