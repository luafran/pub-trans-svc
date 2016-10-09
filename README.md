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
$ kubectl create -f deploy/k8s/pubtrans-all.yaml
$ kubectl get deployments
NAME       DESIRED   CURRENT   UP-TO-DATE   AVAILABLE   AGE
pubtrans   2         2         2            2           3m
$ kubectl get rs
NAME                 DESIRED   CURRENT   AGE
pubtrans-636011768   2         2         5m
$ kubectl get services
NAME         CLUSTER-IP   EXTERNAL-IP   PORT(S)    AGE
kubernetes   10.0.0.1     <none>        443/TCP    4h
pubtrans     10.0.0.72    <nodes>       8888/TCP   3m
$ kubectl get pods --show-labels
NAME                       READY     STATUS    RESTARTS   AGE       LABELS
pubtrans-636011768-fzpn9   1/1       Running   0          46s       app=pubtrans,pod-template-hash=636011768
pubtrans-636011768-xk8m4   1/1       Running   0          46s       app=pubtrans,pod-template-hash=636011768
```

#### Use service

```shell
$ minikube service pubtrans --url
http://192.168.99.100:32395
$ curl http://192.168.99.100:32395/health
```

#### Delete resources
```shell
$ kubectl delete -f deploy/k8s/pubtrans-all.yaml
service "redis-master" deleted
deployment "redis-master" deleted
service "redis-slave" deleted
deployment "redis-slave" deleted
service "pubtrans" deleted
deployment "pubtrans" deleted
```
