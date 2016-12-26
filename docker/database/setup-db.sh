#!/bin/sh

set -e
host="0.0.0.0"
port="27017"
database="CFPs"
collection="cfp_collection"

mkdir -p /var/log/

mongod --fork --logpath /var/log/mongodb.log --bind_ip $host --port $port

#until mongo --host $host --port $port; do
#    >&2 echo "Mongo is unavailable - sleeping"
#    sleep 1
#done

>&2 echo "Mongo is up - running command"
mongoimport --host $host --port $port --db $database --collection $collection --drop --file ./corpus.json
mongo << EOF
use CFPs
db.cfp_collection.createIndex({'\$**': 'text'})
EOF
#mongo --eval "use CFPs;db.CFPs.cfp_collection.createIndex({'$**': 'text'})"
mongod --shutdown
mongod --bind_ip $host --port $port
