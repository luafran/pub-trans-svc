# Public Transportation Service
Web service that extend and wrap NextBus public XML feed as a RESTful HTTP API

### Software Stack

* Python 2.7
* Tornado Web Server
* Redis
* Metrics: Statsd client, Telegraf, InfluxDB and Grafana
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

## Run service locally

### Run service locally using tox

```shell
$ tox -e runservice
```

### Run service locally using Docker Compose

```shell
$ docker-compose build
$ docker-compose up
```

### Build Docker image and push to Docker Hub

Image version is defined in build-and-push-pubtrans.sh

```shell
$ docker login
$ ./build-and-push-pubtrans.sh
```

## Use the service

See [API documentation](doc/api.md)

## Deployment

### Kubernetes (Minikube)

#### Install and start minikube (OSX)

```shell
$ curl -Lo minikube https://storage.googleapis.com/minikube/releases/v0.11.0/minikube-darwin-amd64 && chmod +x minikube && sudo mv minikube /usr/local/bin/
$ curl -Lo kubectl http://storage.googleapis.com/kubernetes-release/release/v1.3.0/bin/darwin/amd64/kubectl && chmod +x kubectl && sudo mv kubectl /usr/local/bin/
$ minikube start
```

#### Deploy service

```shell
$ kubectl create -f deploy/k8s
```

#### Use service

```shell
$ minikube service pubtrans --url
http://192.168.99.100:32395
$ curl http://192.168.99.100:32395/health
```

#### Delete resources
```shell
$ kubectl delete -f deploy/k8s
```
