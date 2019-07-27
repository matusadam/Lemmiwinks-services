# Lemmiwinks-services

Services implementation of Lemmiwinks archiving framework using Sanic web server and aiohttp clients.

This application has been developed as a part of my bachelor's thesis.

### Prerequisites

Python 3.6

Installed Python packages from requirements.txt

Modern and up-to-date Linux distribution

Tor SOCKS proxy running on port 9050

### Install

Clone this project into your local depository

Setup Python virtualenv:

```
cd project_folder
virtualenv venv
```

Install Python packages:

```
pip3 install -r requirements.txt
```

Install Tor:

```
apt install tor
```

If you have problems with Tor setup, visit https://2019.www.torproject.org/docs/debian.html.en

To run the services: `archive_service` folder run `python3.6 service.py` with optional param to specify where the downloader is running: `--download_service_url` (default is http://0.0.0.0:8081) 

In `download_service` run `python3.6 service.py`

Optinally you can `import app from service` for both services. Visit Sanic docs for more details.

## Running the tests

Run: `python3.6 sanic_test.py`. Archive service tests require downloader running: `python3.6 download_service/service.py`

## Built With

* [Sanic](https://github.com/huge-success/sanic) - Asynchronous Web server 
* [Lemmiwinks](https://github.com/nesfit/Lemmiwinks) - Web scrapper and archiving framework


## Authors

* **Viliam Serecun** - [vserecun](https://github.com/vserecun) - Lemmiwinks framework
* **Adam Matus** - [matusadam](https://github.com/matusadam) - Services
