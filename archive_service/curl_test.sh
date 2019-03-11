#!/usr/bin/env bash

curl -i -X POST -H 'Content-Type: application/json' -d '{"urls": ["http://www.seznam.cz"]}' http://0.0.0.0:8080
