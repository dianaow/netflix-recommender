const neo4j = require('neo4j-driver')
const express = require("express")
const cors = require('cors')
const fs = require("fs")
const path = require("path")
const unirest = require("unirest");
const {spawn} = require('child_process');

const app = express()
app.use(cors())
const PORT = process.env.PORT || 8080
const API_ENDPOINT = process.env.REACT_APP_API_ENDPOINT

const protocol="bolt"
const host = "localhost"
const port="7687"
const user="neo4j"
const password="testing"
const driver = neo4j.driver(protocol + "://" + host + ":" + port, neo4j.auth.basic(user, password))

async function run_request(cypher) {
  let results
  let session = driver.session()
  await session.run(cypher)
    .then(r => {
      results = r.records.map(d => d.toObject())
      session.close()
    })
    .catch(e => {
      console.log(e)
      session.close()
    })
  return results

}

app.use(function (req, res, next) {
  res.header("Access-Control-Allow-Origin", "*")
  res.header(
    "Access-Control-Allow-Headers",
    "Origin, X-Requested-With, Content-Type, Accept"
  )

  next()
})

app.get("/actors/:country/:number", async function (req, res, next) {

  let country = req.params.country
  country = country.replace("_", " ")

  const request=`
    MATCH (p:Person)-[rel:ACTED_IN]->(m:Movie)
    WHERE m.country = '${country}'
    WITH p,collect(m.title) as movies,count(*) as total
    RETURN  p.name, movies,total
    ORDER BY total DESC
    LIMIT ${req.params.number}
  `
  let results = await run_request(request)

  return res.send(results)

})

app.get("/path/:from/:to", async function (req, res, next) {

  let from = req.params.from
  from = from.replace("_", " ")
  let to = req.params.to
  to = to.replace("_", " ")

  const request=`
    MATCH (cs:Person { name: "${from}" }),(ms:Person { name: "${to}" }), p = shortestPath((cs)-[:ACTED_IN|:DIRECTED*]-(ms))
    WHERE length(p)> 1 
    RETURN p
  `
  let results = await run_request(request)

  return res.send(results)

})

app.get('/similarity', (req, res) => {
   console.log('Query entered')
   let largeDataSet = []
   let spawn = require('child_process').spawn;
   let python = spawn('python', ['./query.py', req.query.title.replace('%20', ' '), req.query.w1, req.query.w2, req.query.w3, req.query.w4]);

   // collect data from script
   python.stdout.on('data', function (data) {
    console.log('Pipe data from python script ...');
    largeDataSet.push(data);
   });
   // in close event we are sure that stream from child process is closed
   python.on('close', (code) => {
    console.log(`child process close all stdio with code ${code}`);
    // send data to browser
    console.log(largeDataSet.join(""))
    res.send(largeDataSet.join(""))
  })

})

app.use(express.static(path.join(__dirname, "")))

app.listen(PORT, "0.0.0.0", function onStart(err) {
  if (err) {
    console.log(err)
  }
  console.info(
    "==> 🌎 Listening on port %s. Open up http://0.0.0.0:%s/ in your browser.",
    PORT,
    PORT
  )
})

