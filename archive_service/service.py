
import os, re

from schema import ArchiveJsonSchema
from name_generator import ArchiveName
from lemmiwinks_top import ArchiveServiceLemmiwinks

from sanic import Sanic
from sanic import response
from sanic_auth import Auth, User


# Sanic init
app = Sanic()

# Sanic-auth init
app.config.AUTH_LOGIN_ENDPOINT = 'login'
auth = Auth(app)
session = {}
@app.middleware('request')
async def add_session(request):
    request['session'] = session

# TinyDB init
db = TinyDB('db.json')


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

    Logout user in this session and redirect to login page.
    """

    auth.logout_user(request)
    return response.redirect('/login')

@app.route('/archives', methods=['GET'])
@auth.login_required
async def get_archives(request):
    """Archives collection and POST form.

    Gets HTML page with a list of all archives and a POST form for creating
    a new archive from given URL and options.

    :rtype: str
    """
    with open("archive.html", "r", encoding='utf-8') as f:
        archive_html = f.read()

    post_msg = ''
    maff_files = [file for file in os.listdir() if file.endswith(".maff")]
    maffs = "".join(["<li>%s</li>" % file for file in maff_files])

    return response.html(archive_html.format(maffs, post_msg))

@app.route('/archives', methods=['POST'])
@auth.login_required
async def post_archives(request):
    """Create new archive

    Creates new archive from requested URL and options.

    :rtype: str
    """
    with open("archive.html", "r", encoding='utf-8') as f:
        archive_html = f.read()

    post_msg = ''
    maff_files = [file for file in os.listdir() if file.endswith(".maff")]
    maffs = "".join(["<li>%s</li>" % file for file in maff_files])

    url = request.form.get('url')
    archive_name = ArchiveName().full_name()
    aio_archive = ArchiveServiceLemmiwinks([url], archive_name)
    await aio_archive.task_executor()
    post_msg = '<b style="color:green;">Archive created: {}</b>'.format(archive_name)
    return response.html(archive_html.format(maffs, post_msg))

@app.route('/archives/<id>', methods=['GET'])
@auth.login_required
async def archiveItem_get(request, id):
    """Archive item details

    Gets HTML page with archive given by its ID. Contains file download link.

    :param id: 
    :type id: int

    :rtype: str
    """

    result = None
    # tady bude db query result = (SELECT * FROM archivesTable WHERE id==id) nebo tak neco

    if result:
        with open("archiveDetail.html", "r", encoding='utf-8') as f:
            html = f.read()
    else:
        # archive doesnt exist
        with open("notfound.html", "r", encoding='utf-8') as f:
            html = f.read()
        return response.html(html.format(id), status=404)

@app.route('/archives/<id>/<filename>', methods=['GET'])
@auth.login_required
async def archiveFile_get(request, id):
    """Downloads the archive

    Downloads the archive given by its ID. 

    :param id: 
    :type id: int
    :param filename: 
    :type filename: string

    :rtype: str
    """

@app.route('/api/archives', methods=['GET'])
@auth.login_required
async def api_archives_get(request):
    request_json = ArchiveJsonSchema(instance=request.json)
    try:
        request_json.is_valid()
    except ValidationError as e:
        raise InvalidUsage(message=INVALID_USAGE_MESSAGE)
    urls = iter(request.json.get('urls'))
    archive_name = ArchiveName().full_name()
    aio_archive = ArchiveServiceLemmiwinks(urls, archive_name)
    await aio_archive.task_executor()
    resp = {
        "status": "ok",
        "archive_path" : archive_name,
    }
    return response.json(resp)

@app.route('/api/archives', methods=['POST'])
@auth.login_required
async def api_archives_post(request):
    request_json = ArchiveJsonSchema(instance=request.json)
    try:
        request_json.is_valid()
    except ValidationError as e:
        raise InvalidUsage(message=INVALID_USAGE_MESSAGE)
    urls = iter(request.json.get('urls'))
    archive_name = ArchiveName().full_name()
    aio_archive = ArchiveServiceLemmiwinks(urls, archive_name)
    await aio_archive.task_executor()
    resp = {
        "status": "ok",
        "archive_path" : archive_name,
    }
    return response.json(resp)

@app.route('/api/archives/<id>', methods=['GET'])
@auth.login_required
async def api_archiveItem_get(request, name):

    maffs = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.maff')]

    for f in maffs:
        if name in f:
            if request.method == 'GET':
                os.remove(f)   
                return response.json(
                    {"message" : "Archive {} has been deleted".format(f)},
                    status=200
                )

    # archive doesn't exist
    return response.json(
        {"error": "Archive {} not found".format(name)},
        status=404
    )

@app.route('/api/archives/<id>', methods=['DELETE'])
@auth.login_required
async def api_archiveItem_delete(request, name):

    maffs = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.maff')]

    for f in maffs:
        if name in f:
            if request.method == 'DELETE':
                os.remove(f)   
                return response.json(
                    {"message" : "Archive {} has been deleted".format(f)},
                    status=204
                )

    # archive doesn't exist
    return response.json(
        {"error": "Archive {} not found".format(name)},
        status=404
    )


# run Sanic server
if __name__ == "__main__":
  app.run(host="0.0.0.0", port="8080")


