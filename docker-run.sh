#!/usr/bin/env bash

set -e

docker run --name antminer-autotune --rm -tiv $(pwd):/antminer-autotune antminer-autotune
