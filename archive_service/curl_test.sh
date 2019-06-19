#!/usr/bin/env bash

curl -i -X POST -H 'Content-Type: application/json' -d '{"urls": ["http://www.example.org"]}' http://0.0.0.0:8080/archive

curl -i -X GET http://0.0.0.0:8080/archive/20190616T122434_P1N4FJZ9.maff

curl -i -X DELETE http://0.0.0.0:8080/archive/20190616T122434_P1N4FJZ9.maff

curl -i -X POST -H 'Content-Type: application/json' -d '{"urls": ["http://3g2upl4pq6kufc4m.onion/"]}' http://0.0.0.0:8080/archive

curl -i -X POST -H 'Content-Type: application/json' -d '{"urls": ["http://3g2upl4pq6kufc4m.onion/"]}' http://0.0.0.0:8080/archive
