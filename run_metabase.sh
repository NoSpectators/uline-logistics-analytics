#!/bin/bash

# start over
# docker rm -f metabase 2>/dev/null

# docker run -d \                      # run container in detached mode (background)
#   -p 3000:3000 \                     # expose Metabase on localhost:3000
#   --name metabase \                  # name the container "metabase" for easy reference
#   -v metabase-data:/metabase-data \  # persist Metabase internal app data (users, dashboards)
#   -v $(pwd):/data \                  # mount current project folder into container at /data
#   metabase/metabase                  # use the official Metabase Docker image


docker start metabase
