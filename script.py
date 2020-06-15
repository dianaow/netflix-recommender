import sys
import pandas as pd
import pickle

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
from nltk.stem.snowball import SnowballStemmer
from nltk.stem.wordnet import WordNetLemmatizer

# load the data
df = pd.read_csv('./raw-data/netflix_titles.csv')
# convert to datetime
df["date_added"] = pd.to_datetime(df['date_added'])
df['year'] = df['date_added'].dt.year
df['month'] = df['date_added'].dt.month
df['day'] = df['date_added'].dt.day
# convert columns "director, listed_in, cast and country" in columns that contain a real list
# the strip function is applied on the elements
# if the value is NaN, the new column contains a empty list []
df['directors'] = df['director'].apply(lambda l: [] if pd.isna(l) else [i.strip() for i in l.split(",")])
df['categories'] = df['listed_in'].apply(lambda l: [] if pd.isna(l) else [i.strip() for i in l.split(",")])
df['actors'] = df['cast'].apply(lambda l: [] if pd.isna(l) else [i.strip() for i in l.split(",")])
df['countries'] = df['country'].apply(lambda l: [] if pd.isna(l) else [i.strip() for i in l.split(",")])

df = df.reset_index()
df.to_csv('./data/netflix_titles_processed.csv', index=False)

df['actors'] = df['actors'].apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])
#give high rating to top 3 actors
df['actors'] = df['actors'].apply(lambda x: [val + ',' + val if i<=2 else val for i,val in enumerate(x)])
df['actors'] = df['actors'].apply(lambda x: [val.split(',') for val in x])
df['actors'] = df['actors'].apply(lambda x: [item for sublist in x for item in sublist])
df['actors'] = df['actors'].apply(lambda x: ' '.join(x))

df['directors'] = df['directors'].apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])
df['directors'] = df['directors'].apply(lambda x: x * 3) #give higher rating to directors
df['directors'] = df['directors'].apply(lambda x: ' '.join(x))

df['categories'] = df['categories'].apply(lambda x: [str.lower(i.replace(" ", "")) for i in x])
df['categories'] = df['categories'].apply(lambda x: ' '.join(x))

# Build the tfidf matrix with the descriptions
text_content = df['description']
vector = TfidfVectorizer(max_df=0.4,         # drop words that occur in more than X percent of documents
                             min_df=1,      # only use words that appear at least X times
                             stop_words='english', # remove stop words
                             lowercase=True, # Convert everything to lower case 
                             use_idf=True,   # Use idf
                             norm=u'l2',     # Normalization
                             smooth_idf=True # Prevents divide-by-zero errors
                            )
tfidf = vector.fit_transform(text_content)
cosine_similarities = cosine_similarity(tfidf,tfidf)

def countVectorizer(col):
    count = CountVectorizer(analyzer='word',ngram_range=(1, 2),min_df=0, stop_words='english')
    count_matrix = count.fit_transform(df[col])
    cosine_sim = cosine_similarity(count_matrix, count_matrix)
    return cosine_sim

cosine_sim_actors = countVectorizer('actors')
cosine_sim_director = countVectorizer('directors')
cosine_sim_categories = countVectorizer('categories')

outfile = open('./data/cosine_sim_actors.pkl','wb')
pickle.dump(cosine_sim_actors, outfile)
outfile.close()

outfile = open('./data/cosine_sim_director.pkl','wb')
pickle.dump(cosine_sim_director,outfile)
outfile.close()

outfile = open('./data/cosine_sim_categories.pkl','wb')
pickle.dump(cosine_sim_categories,outfile)
outfile.close()

outfile = open('./data/cosine_similarities.pkl','wb')
pickle.dump(cosine_similarities,outfile)
outfile.close()