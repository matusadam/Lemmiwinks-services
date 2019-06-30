
import os
import re

from schema import ArchiveJsonSchema
from name_generator import ArchiveName
from lemmiwinks_top import ArchiveServiceLemmiwinks


from sanic import Sanic
from sanic import response

from sanic_auth import Auth, User


# Sanic init
app = Sanic()

# authentication init
app.config.AUTH_LOGIN_ENDPOINT = 'login'
auth = Auth(app)

session = {}
@app.middleware('request')
async def add_session(request):
    request['session'] = session


# Routes

@app.route('/', methods=['GET'])
async def index(request):
    with open("index.html", "r", encoding='utf-8') as f:
        index_html = f.read()
    return response.html(index_html.format(request.ip))

@app.route('/login', methods=['GET', 'POST'])
async def login(request):
    msg_bad_login = '<b style="color:red;">Incorrect username or password</b>'

    with open("login.html", "r", encoding='utf-8') as f:
        login_html = f.read()

    # TODO: db users
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'xmatus31' and password == '11111':
            user = User(id=1, name=username)
            auth.login_user(request, user)
            return response.redirect('/archive')
        else:
            return response.html(login_html.format(msg_bad_login))

    if request.method == 'GET':
        return response.html(login_html.format(''))

@app.route('/logout')
@auth.login_required
async def logout(request):
    auth.logout_user(request)
    return response.redirect('/login')

@app.route('/archive', methods=['GET', 'POST'])
@auth.login_required
async def archive(request):
    with open("archive.html", "r", encoding='utf-8') as f:
        archive_html = f.read()

    post_msg = ''
    maff_files = [file for file in os.listdir() if file.endswith(".maff")]
    maffs = "".join(["<li>%s</li>" % file for file in maff_files])

    if request.method == 'POST':
        url = request.form.get('url')
        archive_name = ArchiveName().full_name()
        aio_archive = ArchiveServiceLemmiwinks([url], archive_name)
        await aio_archive.task_executor()
        post_msg = '<b style="color:green;">Archive created: {}</b>'.format(archive_name)
        return response.html(archive_html.format(maffs, post_msg))

    if request.method == 'GET':
        return response.html(archive_html.format(maffs, post_msg))

@app.route('/api/archive', methods=['POST'])
@auth.login_required
async def api_archive_post(request):
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


@app.route('/archive/<name>', methods=['GET'])
@auth.login_required
async def archive_elem(request, name):
    # return maff if exists
    files = [f for f in os.listdir('.') if os.path.isfile(f)]
    for f in files:
        if name in f:
            return await response.file(f)

    # archive doesnt exist
    with open("notfound.html", "r", encoding='utf-8') as f:
        notfound_html = f.read()
    
    return response.html(notfound_html.format(name), status=404)

@app.route('/api/archive/<name>', methods=['DELETE'])
@auth.login_required
async def api_archive_delete(request, name):

    maffs = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.maff')]

    for f in maffs:
        if name in f:
            if request.method == 'DELETE':
                os.remove(f)   
                return response.json(
                    {"message" : "Archive {} has been deleted".format(f), "status" : 200},
                    status=200
                )

    # archive doesn't exist
    return response.json(
        {"error": "Archive {} not found".format(name), "status" : 404},
        status=404
    )


# run Sanic server
if __name__ == "__main__":
  app.run(host="0.0.0.0", port="8080")


