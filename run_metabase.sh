#!/bin/bash

docker rm -f metabase 2>/dev/null

docker run -d \
  -p 3000:3000 \
  --name metabase \
  -v metabase-data:/metabase-data \
  -v $(pwd):/data \
  metabase/metabase