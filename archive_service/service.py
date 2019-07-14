
import os, re

from schema import ArchivePostSchema
from name_generator import ArchiveName
from lemmiwinks_top import ArchiveServiceLemmiwinks
from utilities import Archives

from sanic import Sanic
from sanic import response
from sanic_auth import Auth, User
from sanic_token_auth import SanicTokenAuth

# Sanic init
app = Sanic()

# Sanic-auth for browser
app.config.AUTH_LOGIN_ENDPOINT = 'login'
auth = Auth(app)
session = {}
@app.middleware('request')
async def add_session(request):
    request['session'] = session

# Sanic-Token-Auth for API
token_auth = SanicTokenAuth(app, secret_key='Z0SbdsCkNXgrvQSGXqZWTsd0ylWVJasO')

# Sanic routes
@app.route('/', methods=['GET'])
async def get_index(request):
    """get_index

    Main page containing basic information and navigation.

    :rtype: str
    """
    with open("index.html", "r", encoding='utf-8') as f:
        index_html = f.read()
    return response.html(index_html.format(request.ip))

@app.route('/login', methods=['GET'])
async def login(request):
    """Login HTML page

    Login page with login form.
    """

    with open("login.html", "r", encoding='utf-8') as f:
        login_html = f.read()

    return response.html(login_html.format(''))

@app.route('/login', methods=['POST'])
async def login(request):
    """Authenticate a user

    Checks and authenticates a user. Redirects to the main page on corrent login,
    else displays error message.
    """

    msg_bad_login = '<b style="color:red;">Incorrect username or password</b>'

    with open("login.html", "r", encoding='utf-8') as f:
        login_html = f.read()

    username = request.form.get('username')
    password = request.form.get('password')

    if username == 'admin' and password == 'admin':
        user = User(id=1, name=username)
        auth.login_user(request, user)
        return response.redirect('/')
    else:
        return response.html(login_html.format(msg_bad_login))

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
    """Archives collection and POST form.

    Gets HTML page with a list of all archives and a POST form for creating
    a new archive from given URL and options.

    :rtype: str
    """

    with open("archives.html", "r", encoding='utf-8') as f:
        html = f.read()

    msg = ''
    html_archive_list = ''
    archives = Archives()
    for detail in archives.details():
        html_archive_list += '<li><a href="{}">{}</a> - ID: {} - Time created: {} - size: {}</li>'.format(
            detail['href_detail'], detail['name'], detail['aid'], detail['ctime'], detail['size']
        )

    return response.html(html.format(html_archive_list, msg))

@app.route('/archives', methods=['POST'])
@auth.login_required
async def post_archives(request):
    """Create new archive

    Creates new archive from requested URL and options.

    :rtype: str
    """

    form_url = request.form.get('url')
    form_name = request.form.get('name')
    form_forceTor = request.form.get('forceTor')
    archive_name = ArchiveName(name=form_name, urls=form_url)
    aio_archive = ArchiveServiceLemmiwinks([form_url], archive_name.full_name, forceTor=form_forceTor)
    await aio_archive.task_executor()

    with open("archives.html", "r", encoding='utf-8') as f:
        html = f.read()
    msg = '<b style="color:green;">Archive {} created.</b>'.format(archive_name)
    html_archive_list = ''
    archives = Archives()
    for detail in archives.details():
        html_archive_list += '<li><a href="{}">{}</a> - ID: {} - Time created: {} - size: {}</li>'.format(
            detail['href_detail'], detail['name'], detail['aid'], detail['ctime'], detail['size']
        )

    return response.html(html.format(html_archive_list, msg))

@app.route('/archives/<id>', methods=['GET'])
@auth.login_required
async def archiveItem_get(request, id):
    """Archive item details

    Gets HTML page with archive given by its ID. Contains file download link.

    :param id: 
    :type id: int

    :rtype: str
    """

    archives = Archives()
    detail = archives.searchById(id)
    if detail:
        with open("archiveDetail.html", "r", encoding='utf-8') as f:
            html = f.read()
        html = html.format(detail['name'], detail['file'], detail['aid'], detail['ctime'], detail['size'], detail['href_download'])
        return response.html(html)
    else:
        with open("notfound.html", "r", encoding='utf-8') as f:
            html = f.read()
        html = html.format(id)
        return response.html(html, status=404)

    
@app.route('/archives/<id>/<filename>', methods=['GET'])
@auth.login_required
async def archiveFile_get(request, id, filename):
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
        with open("notfound.html", "r", encoding='utf-8') as f:
            html = f.read()
        html.format(id)
        return response.html(html, status=404)


@app.route('/api/archives', methods=['GET'])
@token_auth.auth_required
async def api_archives_get(request):
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
@token_auth.auth_required
async def api_archives_post(request):
    if ArchivePostSchema(request.json).is_valid():
        urls = iter(request.json.get('urls'))
        name = request.json.get('name')
        forceTor = request.json.get('forceTor')
        headers = request.json.get('headers')
        archive_name = ArchiveName(name=name, urls=urls)
        aio_archive = ArchiveServiceLemmiwinks(urls, archive_name.full_name, forceTor=forceTor, headers=headers)
        await aio_archive.task_executor()

        return response.json(None, status=201, headers={'Location': archive_name.href_detail})
    else:
        # bad request
        return response.json(None, status=400)
        
@app.route('/api/archives/<id>', methods=['GET'])
@token_auth.auth_required
async def api_archiveItem_get(request, id):
    """Archive item details

    Gets JSON representation of archive item.

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
@token_auth.auth_required
async def api_archiveItem_delete(request, id):

    archives = Archives()
    detail = archives.searchById(id)
    if detail:
        os.remove(detail['file'])
    return response.json(None, status=204)

@app.route('/api/archives/<id>/<filename>', methods=['GET'])
@token_auth.auth_required
async def api_archiveFile_get(request, id, filename):
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
        return response.json(None, status=404)


# run Sanic server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port="8080")


