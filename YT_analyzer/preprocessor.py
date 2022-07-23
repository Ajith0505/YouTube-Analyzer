import pandas as pd
import numpy as np
from dateutil import parser
import isodate

import nltk
from nltk.corpus import stopwords
from textblob import Word

nltk.download('stopwords')
nltk.download('wordnet')
stop_words = stopwords.words('english')


def preprocess(video_df):
    video_df['durationSecs'] = video_df['duration'].apply(lambda x: isodate.parse_duration(x))
    video_df['durationSecs'] = video_df['durationSecs'].astype('timedelta64[s]')

    cols = ['viewCount', 'likeCount', 'favouriteCount', 'commentCount']
    video_df[cols] = video_df[cols].apply(pd.to_numeric, errors='coerce', axis=1)
    video_df['publishedAt'] = pd.to_datetime(video_df['publishedAt'])
    video_df['year'] = video_df['publishedAt'].dt.year
    video_df['published_month'] = video_df['publishedAt'].dt.month_name(locale='English')

    video_df['Day'] = video_df['publishedAt'].dt.day_name()
    return video_df


def preprocess_comment(comment):
    nltk.download('stopwords')
    nltk.download('wordnet')
    stop_words = stopwords.words('english')
    processed_comment = comment
    processed_comment.replace('[^\w\s]', '')
    processed_comment = " ".join(word for word in processed_comment.split() if word not in stop_words)
    #processed_comment = " ".join(word for word in processed_comment.split() if word not in custom_stopwords)
    processed_comment = " ".join(Word(word).lemmatize() for word in processed_comment.split())
    return(processed_comment)
