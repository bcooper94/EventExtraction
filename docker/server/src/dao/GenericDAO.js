const MongoClient = require('mongodb').MongoClient;

class GenericDAO {
    constructor(host, port, database) {
        this.host = host;
        this.port = port;
        this.database = database;
    }

    async connect(collection) {
        return new Promise(async (resolve, reject) => {
            MongoClient.connect('mongodb://' + this.host + ':' + this.port + '/'
                + this.database, (err, client) => {
                    if (err) return reject(err);

                    return resolve(client.db(this.database));
                });
        });
    }
}

module.exports = GenericDAO;
