const neo4j = require('neo4j-driver')
const fs = require('fs');
const path = require('path');

const protocol="bolt"
const host = "localhost"
const port="7687"
const user="neo4j"
const password="testing"
const driver = neo4j.driver(protocol + "://" + host + ":" + port, neo4j.auth.basic(user, password))

const request_delete =  `MATCH (n) DETACH DELETE n;`

const request_movies = `
  LOAD CSV WITH HEADERS FROM $file AS row 
  MERGE (m:Movie {id: row.show_id,title: row.title}) 
  SET m.director = row.director, 
      m.country = row.country,
      m.date_str = row.date_added, 
      m.release_year = row.release_year, 
      m.rating = row.rating, 
      m.duration = row.duration, 
      m.listed_in = row.listed_in, 
      m.description = row.description,
      m.cast=row.cast,
      m.year = row.year, 
      m.month = row.month, 
      m.day = row.day, 
      m.type = row.type_movie RETURN m
`

const request_persons =`
  MATCH (m:Movie)
  WHERE m.cast IS NOT NULL
  WITH m
  UNWIND split(m.cast, ',') AS actor
  MERGE (p:Person {name: trim(actor)})
  MERGE (p)-[r:ACTED_IN]->(m);
`

const request_categories =`    
  MATCH (m:Movie)
  WHERE m.listed_in IS NOT NULL
  WITH m
  UNWIND split(m.listed_in, ',') AS category
  MERGE (c:Category {name: trim(category)})
  MERGE (m)-[r:IN_CATEGORY]->(c);
` 

const request_type =`    
  MATCH (m:Movie)
  WHERE m.type IS NOT NULL
  WITH m
  MERGE (t:Type {type: m.type})
  MERGE (m)-[r:TYPED_AS]->(t);
`

const request_director =` 
  MATCH (m:Movie)
  WHERE m.director IS NOT NULL
  WITH m
  MERGE (d:Person {name: m.director})
  MERGE (d)-[r:DIRECTED]->(m);
`

const request_countries =` 
  request =""" 
  MATCH (m:Movie)
  WHERE m.country IS NOT NULL
  MERGE (c:Country {name: trim(m.country)})
  MERGE (m)-[:WHERE]->(c);
`

const runQuery = (query, params = {}) => new Promise((resolve, reject) => {
  const session = driver.session(); // <<-- session is only visible inside the promise

  session.run(query, params).then((result) => {
    session.close();
    console.log(`Executed Query - "${query}"`);
    resolve(result);
  }).catch((error) => {
    session.close();
    reject(error);
  });
});

runQuery(request_delete)
  .then(function(script) {
    return runQuery(request_movies, params = { file: 'file:///' + path.join(__dirname, 'data/netflix_titles.csv') })
  }).then(function(script) {
    return runQuery(request_persons)
  }).then(function(script) {
    return runQuery(request_categories)
  }).then(function(script) {
    return runQuery(request_type)
  }).then(function(script) {
    return runQuery(request_director)
  }).then(function(script) {
    return runQuery(request_countries)
  }).catch(e => {
    console.log(e);
  })


