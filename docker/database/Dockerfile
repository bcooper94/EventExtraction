FROM mongo:3.4.0

COPY . /
RUN chmod +x /setup-db.sh
RUN which mongod
#RUN mongod --fork --bind_ip 0.0.0.0 --port 27017
#ENTRYPOINT ./setup-db.sh
#ENTRYPOINT "mongod --bind_ip 0.0.0.0 --port 27017"

#RUN "mongo --port 27017 --host 0.0.0.0 --eval \"db.CFPs.cfp_collection.createIndex({'$**': 'text'})\""