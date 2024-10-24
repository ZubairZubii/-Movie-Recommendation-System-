import pandas as pd
import numpy as np

movies =  pd.read_csv('tmdb_5000_movies.csv')
credits =  pd.read_csv('tmdb_5000_credits.csv')

#print(movies.head())
#print(credits.head()['title'])
movies = movies.merge(credits, on='title')
#print(movies.columns.values)
movies = movies[['movie_id', 'title' , 'overview' , 'genres' , 'keywords' , 'cast' , 'crew']]
#print(movies.head())
#print(movies.isnull().sum())
movies.dropna(inplace=True)
#print(movies.isnull().sum())
#print(movies['genres'][0])

#if uou want to convert string into list then use ast funtion
import ast
def convert_genres_keyword(text):
    gen_array=[]
    for i in ast.literal_eval(text):
        gen_array.append(i['name'])
    return gen_array

movies['genres'] = movies['genres'].apply(convert_genres_keyword)
#print(movies['genres'][1])
#print(movies['keywords'][0])
movies['keywords'] = movies['keywords'].apply(convert_genres_keyword)
#print(movies['keywords'][0])

#print(movies['cast'][0])

def convert_crew(text):
    gen_array=[]
    for i in ast.literal_eval(text):
            if i['job'] =='Director':
                gen_array.append(i['name'])
    return gen_array

movies['crew'] = movies['crew'].apply(convert_crew)
#print(movies['crew'][0])
#print(movies.head())

#print(movies['overview'][0])
movies['overview'] = movies['overview'].apply(lambda x: x.split())
#print(movies['overview'][0])

movies['genres'] = movies['genres'].apply(lambda x : [i.replace(' ','') for i in x])
movies['keywords'] = movies['keywords'].apply(lambda x : [i.replace(' ','') for i in x])
movies['cast'] = movies['cast'].apply(lambda x : [i.replace(' ','') for i in x])
movies['crew'] = movies['crew'].apply(lambda x : [i.replace(' ','') for i in x])

#print(movies.head())
movies['tags'] = movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']
new_movies = movies[['movie_id' , 'title' , 'tags']]
#print(movies['tags'][0] )
#dataframe list of string
new_movies  = pd.DataFrame(new_movies)
new_movies['tags'] = new_movies['tags'].apply(lambda x : " ".join(x))
#print(new_movies['tags'][0])
new_movies['tags'] = new_movies['tags'].apply(lambda x : x.lower())
#print(new_movies['tags'][0])

#from sklearn.feature_extraction.text import CountVectorizer
#c = CountVectorizer(max_features=5000 , stop_words='english')
#vector  = c.fit_transform(new_movies['tags']).toarray()
#print(vector[0])
#print(c.get_feature_names_out())

import nltk
from nltk.stem.porter import PorterStemmer
st = PorterStemmer()
def stem(text):
    s = []
    for i in text.split():
        s.append(st.stem(i))
    return ' '.join(s)

new_movies['tags'] = new_movies['tags'].apply(stem)
from sklearn.feature_extraction.text import CountVectorizer

c = CountVectorizer(max_features=5000 , stop_words='english')
vector  = c.fit_transform(new_movies['tags']).toarray()
#print(vector[0])
#print(c.get_feature_names_out())

#print(new_movies.iloc[0])
from sklearn.metrics.pairwise import cosine_similarity
simmilarity = cosine_similarity(vector)
#print(simmilarity)
def recommend(movie):
    movie_index = new_movies[new_movies['title'] == movie].index[0]
    distance =simmilarity[movie_index]
    movie_list = sorted(list(enumerate(distance)) , reverse=True ,key=lambda x: x[1])[1:6]
    recomm_movie=[]
    recomm_movie_path=[]
    for i in movie_list:
        movieid = new_movies.iloc[i[0]].movie_id
        recomm_movie.append(new_movies.iloc[i[0]].title)
        recomm_movie_path.append(fetch_poster(movieid))
    return recomm_movie,recomm_movie_path


import requests
#recommend('Avatar')
def fetch_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=9000b5b1d98bb152aa1f762fecb8e38d&language=en-US'.format(movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w185/" + data['poster_path']


import streamlit as st

st.markdown(
    """
    <style>
    body {
        background-color: #121212; 
        color: #F0F0F0;
        font-family: 'Roboto', sans-serif;
    }
    .title {
        font-size: 48px;
        color: #FFFFFF;
        text-align: center;
        margin: 20px 0;
    }
    .recommend-btn {
        background-color: #FF6347;
        border: none;
        color: white;
        padding: 12px 24px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 8px 0;
        cursor: pointer;
        border-radius: 8px;
        transition: 0.3s;
        width: 200px;
        font-weight: bold;
    }
    .recommend-btn:hover {
        background-color: #FF4500;
    }
    .card {
        padding: 20px;
        border-radius: 15px;
        background-color: #1e1e1e;
        text-align: center;
        color: white;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        transition: 0.3s;
    }
    .card:hover {
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.4);
    }
    .footer {
        text-align: center;
        padding: 20px;
        margin-top: 30px;
        color: #B0B0B0;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title
st.markdown("<h1 class='title'>🎬 Movie Recommendation System 🎥</h1>", unsafe_allow_html=True)

# Selectbox for movie selection
selected_movie = st.selectbox(
    'Select a movie to get recommendations:',
    (new_movies['title'].values)
)

# Button for recommendations
if st.button('Recommend', key="recommend-btn"):
    names, posters = recommend(selected_movie)
    cols = st.columns(5)
    
    for i in range(5):
        with cols[i]:
            st.markdown(
                f'''
                <div class="card">
                    <p style="font-size: 18px; font-weight: bold;">{names[i]}</p>
                    <img src="{posters[i]}" width="150" style="border-radius: 10px;">
                </div>
                ''',
                unsafe_allow_html=True
            )

# Add footer
st.markdown(
    """
    <footer class='footer'>
        <p>Powered by TMDB API | Designed by Zubair Ali</p>
    </footer>
    """, 
    unsafe_allow_html=True
)
