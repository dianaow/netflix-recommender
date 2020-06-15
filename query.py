import sys
import pandas as pd
from functools import reduce
import pickle
# import initial_load

# ## import pickled files of algorithm results
# cosine_sim_actors = initial_load.cosine_sim_actors
# cosine_sim_director = initial_load.cosine_sim_director
# cosine_sim_categories = initial_load.cosine_sim_categories
# cosine_similarities = initial_load.cosine_similarities

# ## import csv containing urls of posters
# df_photos = initial_load.photo_dataAll

cosine_sim_actors = pickle.load( open( "./data/cosine_sim_actors.pkl", "rb" ) )
cosine_sim_director = pickle.load( open( "./data/cosine_sim_director.pkl", "rb" ) )
cosine_sim_categories = pickle.load( open( "./data/cosine_sim_categories.pkl", "rb" ) )
cosine_similarities = pickle.load( open( "./data/cosine_similarities.pkl", "rb" ) )

df_photos = pd.DataFrame()
for i in range(1000, 7000, 1000):
  photo_data = pickle.load( open( './raw-data/photo_url_' + str(i) + '.pkl', "rb" ) )
  df_photos = pd.concat([df_photos, photo_data])

## import original data instead of dataframe of processed data
df = pd.read_csv('./data/netflix_titles_processed.csv')

titles = df['title']
indices= pd.Series(df.index, index=df['title'])

def get_recommendations(title, cosine_sim, col):
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:31]
    movie_indices = [i[0] for i in sim_scores]
    movie_scores = [i[1] for i in sim_scores]
    movies = df.iloc[movie_indices]
    movies['scores'] = movie_scores
    if(col == 'soup'):
        return movies[['index', 'show_id', 'title', 'actors', 'directors', 'categories', 'scores']]
    else:
        return movies[['index', 'show_id', 'title', col, 'scores']]

def improved_recommendations(title, weights):
    df_actors = get_recommendations(title, cosine_sim_actors, 'actors').rename(columns={'scores': 'actor_score'})
    df_directors = get_recommendations(title, cosine_sim_director, 'directors').rename(columns={'scores': 'director_score'})
    df_categories = get_recommendations(title, cosine_sim_categories, 'categories').rename(columns={'scores': 'category_score'})
    df_description = get_recommendations(title, cosine_similarities, 'description').rename(columns={'scores': 'description_score'})
    data_frames = [df_actors, df_directors, df_categories, df_description]
    df_merged = reduce(lambda  left,right: pd.merge(left,right,on=['index', 'title', 'show_id'], how='outer'), data_frames)
    df_merged = df_merged.fillna(0)
    df_merged['scores'] = df_merged['actor_score'] * float(weights['wActor']) + df_merged['director_score'] * float(weights['wDirector']) + df_merged['category_score'] * float(weights['wCategory']) + df_merged['description_score'] * float(weights['wDescription'])
    df_merged = df_merged.sort_values('scores', ascending=False).reset_index(drop=True).head(10)

    # extract image url
    for i,row in df_merged.iterrows():
        try:
          image = df_photos[(df_photos['show_id'] == row.show_id)]['url'].values
        except:
          image = ""
        df_merged.loc[i, 'image'] = image
        
    return df_merged


TITLE = sys.argv[1]
weights = { 'wActor': sys.argv[2], 'wDirector': sys.argv[3], 'wCategory': sys.argv[4], 'wDescription': sys.argv[5] }

recommended_titles = improved_recommendations(TITLE, weights)
json = recommended_titles.to_json(orient='records')

print(json)