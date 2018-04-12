const MongoClient = require('mongodb').MongoClient;
const CFP = require('../models/CFP');
const GenericDAO = require('./GenericDAO');

const cfpCollection = 'cfp_collection';

class CFPDAO extends GenericDAO {
    constructor(host, port, database) {
        super(host, port, database);
    }

    async getAllCfps() {
        return new Promise(async (resolve, reject) => {
            try {
                let client = await this.connect(cfpCollection);
                client.collection(cfpCollection).find().toArray((err, results) => {
                    if (err) reject(err);

                    resolve(results.map((cfp) => new CFP(cfp)));
                });
            } catch (ex) {
                console.error('Failed to get all CFPs: ' + ex);
                reject(ex);
            }
        });
    }
}

module.exports = CFPDAO;
