#!/usr/bin/env bash

set -e

docker build -t python:latest -t python:v1.0 https://github.com/brettvitaz/docker.git#master:python
docker build -t antminer-autotune .
