#!/usr/bin/env bash

curl -i -X POST -H 'Content-Type: application/json' -d '{"urls": [{"url":"http://example.org"}, {"url": "http://httpbin.org/get"}]}' http://0.0.0.0:8080
