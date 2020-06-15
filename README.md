
## A Netflix movie &amp; TV show recommender system

### Set up instructions

#### Initial Data Processing

1) To create a virtual environment in python 3.6

`virtualenv --python=/usr/bin/python3.6 <path/to/new/virtualenv/>`

2) Activate the environment and install all the packages available in the requirement.txt file.

`source <path/to/new/virtualenv>/bin/activate
pip install -r <path/to/requirement.txt>`

3) To create and store recommendation system algorithm output files (This only needs to be run once)

`python script.py`


#### Launch App

4) Install all required packages and dependencies

`npm install`

5) Start up the web server

`node server.js`

6) Open http://localhost:8080 to view the webpage in the browser. You may begin querying for similar Netflix shows through the search bar.

![alt text](https://github.com/dianaow/netflix-recommender/raw/master/example.gif "Demo")