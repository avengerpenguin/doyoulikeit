#!/bin/bash

set -ex -o pipefail

tofu -chdir=infra apply
REGISTRY=$(tofu -chdir=infra output -json | jq -r .registry_endpoint.value)
VERSION=$(date +%s)

docker build --platform=linux/amd64 -t "$REGISTRY/doyoulikeit:$VERSION" .
docker tag "$REGISTRY/doyoulikeit:$VERSION" "$REGISTRY/doyoulikeit:latest"
docker push "$REGISTRY/doyoulikeit:$VERSION"
docker push "$REGISTRY/doyoulikeit:latest"

tofu -chdir=infra apply -var "docker_tag=${VERSION}"
