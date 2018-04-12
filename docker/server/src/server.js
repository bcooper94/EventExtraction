const express = require('express');
const CFPDAO = require('./dao/CFPDAO');
const cors = require('cors');

const app = express();
const port = 5000;

const dbHost = '172.18.0.1';
const dbPort = 27000;
const database = 'CFPs';

const CfpDao = new CFPDAO(dbHost, dbPort, database);

app.use(cors());

app.get('/get-all-cfps', async (req, res) => {
    try {
        res.send(await CfpDao.getAllCfps());
    } catch (ex) {
        res.send(ex);
    }
});

app.listen(port, () => console.log('CFP app listening on port ' + port));
