#!/usr/bin/env node

const express = require('express');
const fs = require('fs');
const bodyParser = require('body-parser');

const stdout = process.stdout;
const stderr = process.stderr;
const app = express();

const webPort = 8080;
const inputFile = "../latency.json";

const stream = fs.createReadStream(inputFile, {flags: 'r', encoding: 'utf-8'});
let jsonBuff = "";
let latencyMatrix = [];
let nodes = [];

stream.on('data', function(d) {
    jsonBuff += d.toString(); // when data is read, stash it in a string buffer
});

stream.on('end', () => {
    const raw = JSON.parse(jsonBuff);
    for (var i = 0; i < raw.length; i++)
        nodes.push(raw[i][0]); // store labels
    let timeline = {};
    const getFrame = t => {
        if (timeline[t] === undefined) {
            let frame = [];
            for (var i = 0; i < raw.length; i++) {
                let row = [];
                for (var j = 0; j < raw[i][1].length; j++) {
                    row.push({
                        cnt: 0,
                        sum: 0,
                    });
                }
                frame.push(row);
            }
            timeline[t] = frame;
        }
        return timeline[t];
    };
    for (let i = 0; i < raw.length; i++) {
        for (let j = 0; j < raw[i][1].length; j++) {
            raw[i][1][j].forEach(e => {
                const t = Math.floor(e[0]);
                let agg = getFrame(t - t % 60);
                agg[i][j].cnt++;
                agg[i][j].sum += e[1];
            });
        }
    }
    latencyMatrix = [];
    Object.entries(timeline).forEach(([k, v]) => {
        const avg = v.map(r => r.map(c => c.sum / c.cnt));
        latencyMatrix.push({
            t: k,
            avg,
        });
    });
    latencyMatrix.sort((a, b) => a.t - b.t);
    stdout.write(`finished loading ${inputFile}\n`);
});

app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

app.use(express.static('public'));

app.get('/latency', (req, res) => {
    let data = {};
    if (req.query.idx === undefined) {
        res.send({n: latencyMatrix.length, nNode: latencyMatrix[0].avg.length});
        return;
    }
    const idx = parseInt(req.query.idx);
    if (idx == NaN || idx < 0 || idx >= latencyMatrix.length) {
        res.end();
        return;
    }
    res.send(latencyMatrix[idx]);
});


app.listen(webPort, () => {
    stderr.write(`listening at localhost:${webPort}\n`);
})

