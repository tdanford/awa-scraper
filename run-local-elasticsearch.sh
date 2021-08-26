#!/bin/bash 

DIR=$( python -m awa.search `dirname $0` ) 
echo $DIR
VERSION="7.14.0"
DOCKER_IMAGE="docker.elastic.co/elasticsearch/elasticsearch:$VERSION" 

echo "Using $DIR as data directory for Elasticsearch $VERSION" 
docker run --rm  -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" -v "$DIR:/usr/share/elasticsearch/data" $DOCKER_IMAGE 
