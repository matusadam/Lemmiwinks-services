import os

from schema import ArchiveJsonSchema
from name_generator import ArchiveName
from lemmiwinks_top import ArchiveServiceLemmiwinks
from exception_messages import INVALID_USAGE_MESSAGE

from jsonschema import ValidationError
from sanic.exceptions import InvalidUsage

async def archive_post_response(request):
    # TODO: validate request
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
    return resp

async def archive_get_response(request):
    with open("archive.html", "r", encoding='utf-8') as f:
        archive_page = f.read()
    maff_files = [file for file in os.listdir() if file.endswith(".maff")]
    formated = "".join(["<li>%s</li>" % file for file in maff_files])
    archive_page = archive_page % formated
    return archive_page

async def info_page_response(request):
    with open("index.html", "r", encoding='utf-8') as f:
        info_page = f.read()
    info_page = info_page % request.ip
    return info_page