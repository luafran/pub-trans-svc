FROM python:2.7-alpine

MAINTAINER Luciano Afranllie <luafran@gmail.com>

ENV INSTALL_DIR /opt/pubtrans
ENV PYTHONPATH /opt

RUN apk add --no-cache ca-certificates musl-dev gcc make openssl-dev curl-dev

ADD pubtrans/ ${INSTALL_DIR}
ADD requirements.txt ${INSTALL_DIR}/requirements.txt
RUN pip install -Ur ${INSTALL_DIR}/requirements.txt

# Expose port
EXPOSE 80

# Run app
CMD python ${INSTALL_DIR}/application.py --port 80
