#!/bin/bash

build_number=$1
if [ -z ${build_number} ]; then
    build_number=0
fi

registry_user="luafran"
image_name="pubtrans"

commit_id=$(git rev-parse HEAD)
# version="${commit_id}.${build_number}"
version="0.0.5.${build_number}"

image_tag=${registry_user}/${image_name}:${version}

echo "image_tag: ${image_tag}"

docker build -f Dockerfile -t ${image_tag} .

docker push ${image_tag}
