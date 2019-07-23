#!/usr/bin/env bash

curl -i -H -H "Authorization: Token Z0SbdsCkNXgrvQSGXqZWTsd0ylWVJasO" http://0.0.0.0:8080/api/archives
# API GET not auth
curl -i -X GET http://0.0.0.0:8080/api/archives
curl -i -X GET http://0.0.0.0:8080/api/archives?name=Reddit&skip=0&limit=5
curl -i -X GET http://0.0.0.0:8080/api/archives/id

# API GET with auth
curl -i -X GET -H "Authorization: Token Z0SbdsCkNXgrvQSGXqZWTsd0ylWVJasO" http://0.0.0.0:8080/api/archives
curl -i -X GET -H "Authorization: Token Z0SbdsCkNXgrvQSGXqZWTsd0ylWVJasO" 'http://0.0.0.0:8080/api/archives?name=Reddit&skip=0&limit=5'
curl -i -X GET -H "Authorization: Token Z0SbdsCkNXgrvQSGXqZWTsd0ylWVJasO" http://0.0.0.0:8080/api/archives/id


# API POST with auth
curl http://0.0.0.0:8080/api/archives -i -H "Content-Type: application/json" -H "Authorization: Token Z0SbdsCkNXgrvQSGXqZWTsd0ylWVJasO" -X POST -d '{"urls" : ["http://www.wikipedia.org"], "name" : "WikiGerman", "forceTor" : false, "headers" : {"Accept-Language":"de"}}'


# API DELETE
curl -i -X DELETE http://0.0.0.0:8080/api/archives/id -H "Authorization: Token Z0SbdsCkNXgrvQSGXqZWTsd0ylWVJasO"

# API download
curl http://0.0.0.0:8080/api/archives/27movv2r/Wikipedia_27movv2r.maff -i -H "Authorization: Token Z0SbdsCkNXgrvQSGXqZWTsd0ylWVJasO"