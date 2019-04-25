#!/usr/bin/env bash

curl -i -X POST -H 'Content-Type: application/json' -d '{"urls": ["http://www.example.org"], "useTor" : true}' http://0.0.0.0:8080/archive
