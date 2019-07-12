
import os, re

from schema import ArchivePostSchema
from name_generator import ArchiveName
from lemmiwinks_top import ArchiveServiceLemmiwinks
from utilities import Archives


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
    aio_archive = ArchiveServiceLemmiwinks([form_url], archive_name.full_name)
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
        return await response.file(filename)
    else:
        with open("notfound.html", "r", encoding='utf-8') as f:
            html = f.read()
        html.format(id)
        return response.html(html, status=404)


@app.route('/api/archives', methods=['GET'])
@auth.login_required
async def api_archives_get(request):
    """Archives collection.

    Gets JSON collection of all archives. Use query params.

    :rtype: json
    """

    archives = Archives()
    search_name = request.args['name'][0]
    skip = int(request.args['skip'][0])
    limit = int(request.args['limit'][0])
    details = archives.searchByName(request.args['name'][0])
    details = details[skip:skip+limit]

    return response.json(details)

@app.route('/api/archives', methods=['POST'])
@auth.login_required
async def api_archives_post(request):
 
    if ArchivePostSchema(request.json).is_valid():
        json_urls = iter(request.json.get('urls'))
        json_name = request.json.get('name')
        json_forceTor = request.json.get('forceTor')
        archive_name = ArchiveName(name=json_name, urls=json_urls)
        aio_archive = ArchiveServiceLemmiwinks(json_urls, archive_name.full_name)
        await aio_archive.task_executor()

        return response.json(None, status=201, headers={'Location': })
    else:
        # 400

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


