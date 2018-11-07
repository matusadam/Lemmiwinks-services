from sanic import Sanic
from sanic.response import html
from sanic.response import json

app_test = Sanic()

@app_test.route("/")
async def welcome(request):
  return html("<h1>Welcome</h1>")

@app_test.route("/archive")
async def archive_query(request):
  query = request.args
  if "uri" not in query:
    return json({"query_uri":None})
  else:
    return json({"query_uri":query["uri"]})

if __name__ == "__main__":
  app_test.run(host="0.0.0.0", port="80")


