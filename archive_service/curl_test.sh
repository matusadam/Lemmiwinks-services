#!/usr/bin/env bash

curl -i -H -H "Authorization: Basic YWRtaW46YWRtaW4=" http://0.0.0.0:8080/api/archives
# API GET not auth
curl -i -X GET http://0.0.0.0:8080/api/archives
curl -i -X GET "http://0.0.0.0:8080/api/archives?name=Reddit&skip=0&limit=5"
curl -i -X GET http://0.0.0.0:8080/api/archives/id

# API GET with auth
curl -i -X GET -H "Authorization: Basic YWRtaW46YWRtaW4=" http://0.0.0.0:8080/api/archives
curl -i -X GET -H "Authorization: Basic YWRtaW46YWRtaW4=" 'http://0.0.0.0:8080/api/archives?name=Reddit&skip=0&limit=5'


# API POST with auth

# skibila.cz accept lang pl
curl http://0.0.0.0:8080/api/archives -i -H "Content-Type: application/json" -H "Authorization: Basic YWRtaW46YWRtaW4=" -X POST -d '{"urls" : ["http://www.skibila.cz"], "name" : "SkiBilaLangPL", "forceTor" : false, "headers" : {"Accept-Language":"pl"}}'


# API DELETE
curl -i -X DELETE http://0.0.0.0:8080/api/archives/id -H "Authorization: Basic YWRtaW46YWRtaW4="