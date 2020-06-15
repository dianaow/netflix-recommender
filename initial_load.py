import pickle
import boto3
import boto3.session
import pandas as pd

cred = boto3.Session().get_credentials()
ACCESS_KEY = cred.access_key
SECRET_KEY = cred.secret_key
SESSION_TOKEN = cred.token  ## optional

s3client = boto3.client('s3', 
                        aws_access_key_id = ACCESS_KEY, 
                        aws_secret_access_key = SECRET_KEY, 
                        aws_session_token = SESSION_TOKEN
                       )

BUCKET = 'netflix-neo4j'

response = s3client.get_object(Bucket=BUCKET, Key='cosine_sim_actors.pkl')
body = response['Body'].read()
cosine_sim_actors = pickle.loads(body)

response = s3client.get_object(Bucket=BUCKET, Key='cosine_sim_director.pkl')
body = response['Body'].read()
cosine_sim_director = pickle.loads(body)

response = s3client.get_object(Bucket=BUCKET, Key='cosine_sim_categories.pkl')
body = response['Body'].read()
data = pickle.loads(body)

response = s3client.get_object(Bucket=BUCKET, Key='cosine_similarities.pkl')
body = response['Body'].read()
data = pickle.loads(body)


photo_dataAll = pd.DataFrame()
for i in range(1000, 7000, 1000):
  response = s3client.get_object(Bucket=BUCKET, Key='photo_url_' + str(i) + '.pkl')
  body = response['Body'].read()
  photo_data = pickle.loads(body)
  photo_dataAll = pd.concat([photo_dataAll, photo_data])


print('completed data import')