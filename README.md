# Public Transportation Service
Web service that extend and wrap NextBus public XML feed as a RESTful HTTP API

### Software Stack

* Python 2.7
* Tornado Web Server [Site](http://www.tornadoweb.org/en/stable/)
* Redis
* Docker and Docker Compose

### Other tools
* tox
* nose

## Development Environment Setup (Mac OSX)

### Install Python and PIP, tox, virtualenv and virtualenvwrapper

```shell
$ brew install python
$ sudo pip install --upgrade pip
$ pip install tox virtualenv virtualenvwrapper
$ cp ~/.bash_profile ~/.bash_profile.bak
$ printf '\n%s\n%s\n%s' '# virtualenv' 'export WORKON_HOME=~/virtualenvs' \
'source /usr/local/bin/virtualenvwrapper.sh' >> ~/.bash_profile
```

### Install Docker Engine and Docker Compose


## Developer Tools

### Run pylint (static analysis)

Report: ci/reports/pylint/index.html

```shell
$ tox -e pylint
```

### Run flake8 (static analysis)
Report: ci/reports/flake8/index.txt

```shell
$ tox -e flake8
```

### Run unit tests
Coverage report in ci/reports/unit-tests/coverage/index.html
Test results in xunit format in ci/reports/unit-tests/nosetests.xml

```shell
$ tox -e unit-tests
```

### Regenerate environment

```shell
$ tox -r -e <env>
```

## Run service

### Run service using tox

```shell
$ tox -e runservice
```

### Run service using Docker Compose

```shell
$ docker-compose build
$ docker-compose up
```

## Use The Service

### Send a request to service health

```shell
$ curl --proxy '' -H 'Accept: application/json' 'http://localhost:8888/health' | python -m json.tool
{
    "status": {
        "details": [],
        "health": [
            0,
            "OK"
        ],
        "service": "pubtrans",
        "version": "0.0.1"
    }
}
```

### Get Agencies

```shell
$ curl --proxy '' -H 'Accept: application/json' 'http://localhost:8888/v1/agencies' | python -m json.tool
{
    "agencies": [
        {
            "regionTitle": "California-Northern",
            "tag": "actransit",
            "title": "AC Transit"
        },
        ...
        {
            "regionTitle": "Pennsylvania",
            "tag": "york-pa",
            "title": "York College"
        }
    ]
}
```
