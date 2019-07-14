#!/usr/bin/env bash

docker run -it --rm -v $(pwd)/data:/app/data -p 5000:5000 docker.k8s.home/speedport $@
