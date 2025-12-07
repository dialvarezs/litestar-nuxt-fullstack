#!/usr/bin/env bash

tag_prefix="app"
date=$(date '+%Y%m%d')

build_image() {
  local target=$1
  local dir=$2
  podman build --pull=newer -t "${tag_prefix}_${target}:${date}" -t "${tag_prefix}_${target}:latest" "${dir}"
}

build_target=${1:-all}

case $build_target in
  api)
    build_image "api" ../app_api/
    ;;
  web)
    build_image "web" ../app_web/
    ;;
  all)
    build_image "api" ../app_api/
    build_image "web" ../app_web/
    ;;
  *)
    echo "Usage: $0 [api|web|all]"
    exit 1
    ;;
esac
