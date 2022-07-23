import streamlit as st
import pandas as pd
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from wordcloud import STOPWORDS, WordCloud
from googleapiclient.discovery import build
import helper
import panel as pn
pn.extension('tabulator')
from bokeh.plotting import figure
import hvplot
import hvplot.pandas
import holoviews as hv
hv.extension('bokeh', logo=False)
import plotly.express as px
import preprocessor
from textblob import Word, TextBlob
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
classifier = pipeline('sentiment-analysis','bert-base-multilingual-uncased-sentiment')
summarizer = pipeline('summarization')
from PIL import Image

image = Image.open('youtube-analytics-banner.png')
st.image(image)
#st.header('Youtube Analyzer')


api_key = st.text_input('You got to input the api key')
if api_key:
    youtube = build('youtube', 'v3', developerKey=api_key)

user_menu=st.radio(
     "Select an option",
     ('Analysis and Download Video Transcript','Multiple Channel Analysis'))

if user_menu=='Multiple Channel Analysis':

    ids = st.text_input('You got to input the channel id')
    channel_ids=ids.split(',')
    st.write('The channel ids are', channel_ids)
    
    st.sidebar.header('Functionalities')
    channel_statistics = helper.get_channel_stats(youtube, channel_ids)
    channel_data = pd.DataFrame(channel_statistics)
    check = st.checkbox('Show Table ')
    if check:
        st.dataframe(channel_data)
    channel_data['Subscribers'] = pd.to_numeric(channel_data['Subscribers'])
    channel_data['Views'] = pd.to_numeric(channel_data['Views'])
    channel_data['Total_videos'] = pd.to_numeric(channel_data['Total_videos'])
    options=channel_data['Channel_name'].unique()
    options.sort()
    #st.write('The channel names are',options)

    check = st.sidebar.checkbox('Show Barchart ')

    if check:
        chart_menu = st.radio(
            "Select an option",
            ('Subscribers', 'Views','Total_videos'))
        if chart_menu=='Subscribers':
            fig = px.bar(channel_data, x="Channel_name", y="Subscribers", title='bar chart ')
            st.plotly_chart(fig, use_container_width=True)
        elif chart_menu=='Views':
            fig = px.bar(channel_data, x="Channel_name", y="Views", title='bar chart ')
            fig.update_traces(marker_color='red')
            st.plotly_chart(fig, use_container_width=True)
        elif chart_menu=='Total_videos':
            fig = px.bar(channel_data, x="Channel_name", y="Total_videos", title='bar chart ')
            fig.update_traces(marker_color='green')
            st.plotly_chart(fig, use_container_width=True)
    video_df = pd.DataFrame()
    check1 = st.sidebar.checkbox('Show the Video details table ')
    if check1:
        for c in channel_data['Channel_name'].unique():
            print("Getting video information from channel: " + c)
            playlist_id = channel_data.loc[channel_data['Channel_name'] == c, 'playlist_id'].iloc[0]
            video_ids = helper.get_video_ids(youtube, playlist_id)
        # get video data
            video_data = helper.get_video_details(youtube, video_ids)

        # append video data together and comment data toghether
            video_df = video_df.append(video_data, ignore_index=True)
        video_df = preprocessor.preprocess(video_df)
        #options = video_df['channelTitle'].unique()
        st.subheader('Video Info Table')
        st.dataframe(video_df)


    check2 = st.sidebar.checkbox('Show Barchart for Video Count for each Year ')

    if check2:
        option = st.selectbox(
            'select the channel',options)
        st.subheader('Video uploads count of '+option+' for each Year')
        group_df = video_df[video_df['channelTitle']==option].groupby('year')['title'].count().reset_index().rename(columns={'title': 'Count'})
        group_df['year'] = group_df['year'].astype(int)
        fig = px.bar(group_df, x="year", y="Count", title='bar chart ')
        fig.update_traces(marker_color='red')
        st.plotly_chart(fig, use_container_width=True)
    #options = video_df['channelTitle'].unique()
    #st.write(options)
    check3 = st.sidebar.checkbox('Show Barchart for Video Count with respect to the months in each year ')

    if check3:
    #option_1 = st.multiselect(
    #    'What are your favorite colors',
    #   ['Green', 'Yellow', 'Red', 'Blue'],
    #    ['Yellow', 'Red'])

    #st.write('You selected:', option_1)

        option1 = st.multiselect('channel names',options,options)
        month_df = video_df[video_df['channelTitle'].isin(option1)].groupby(['year', 'published_month'])['title'].count().reset_index().rename(columns={'title': 'Count'})
        #st.dataframe(month_df)



        options1=month_df['year'].unique()
        #st.write(options1)
        option2 = st.selectbox('select the year', options1)
        st.subheader('Video uploads Count with respect each months in each year')



        fig = px.bar(month_df[month_df['year'] == option2], x='published_month', y='Count', title='bar chart ')
        fig.update_traces(marker_color='green')
        fig.update_layout(xaxis_title='published_month_' + str(option2), yaxis_title='Count')
        st.plotly_chart(fig, use_container_width=True)

    check4= st.sidebar.checkbox('Show the bar chart for how often or the days in which they upload videos in a week')
    if check4:
        channel_name=video_df['channelTitle'].unique()
        channel_name.sort()
        option4=st.selectbox(
            'select the channel_name', channel_name)
        day_df = video_df[video_df['channelTitle'] == option4]['Day'].value_counts().reset_index().rename(
            columns={'index': 'Day_name', 'Day': 'count'})
        fig = px.bar(day_df, x="Day_name", y="count", title='bar chart ')
        fig.update_traces(marker_color='red')
        st.plotly_chart(fig, use_container_width=False)

    check5=st.sidebar.checkbox('Show violin plot for Duration secs,view count across the channels')
    if check5:
        columns=st.radio('Select the column',('Duration','Views'))
        if columns=='Duration':
            fig = px.violin(video_df, x='channelTitle', y="durationSecs", color="channelTitle", box=True,
                            # draw box plot inside the violin
                            points='all',  # can be 'outliers', or False
                            )
            st.plotly_chart(fig, use_container_width=False)

        if columns=='Views':
            fig = px.violin(video_df, x='channelTitle', y="viewCount", color="channelTitle", box=True,
                            # draw box plot inside the violin
                            points='all',  # can be 'outliers', or False
                            )
            st.plotly_chart(fig, use_container_width=False)



    check6 = st.sidebar.checkbox('Show scatter plot for Duration secs v/s like count,comment count,view count')

    if check6:
        cols=['viewCount','likeCount','commentCount']
        option3 = st.selectbox(
            'select the channel', cols)
        fig = px.scatter(video_df, x="durationSecs", y=option3, title='scatterplot')
        fig.update_traces(marker_color='yellow')
        fig.update_traces(marker=dict(size=12,line=dict(width=2,color='DarkSlateGrey')),selector=dict(mode='markers'))
        st.plotly_chart(fig, use_container_width=True)

    check7 = st.sidebar.checkbox('Show countplot of top ten tags used in their respective channel')

    if check7:
        titles = st.selectbox(
            'select the particular channel', options)
        tag_df=helper.get_tag(video_df[video_df['channelTitle']==titles])
        fig = px.bar(tag_df, x="Tags", y="count", title='bar chart ')
        fig.update_traces(marker_color='yellow')
        st.plotly_chart(fig, use_container_width=True)

    check8 = st.sidebar.checkbox('Show top five videos')

    if check8:
        cols = ['viewCount', 'likeCount', 'favouriteCount', 'commentCount']
        choice = st.multiselect('channel_Titles', options, options)
        titles = st.selectbox(
            'Select the  Channel', cols)
        samp_df = video_df[video_df['channelTitle'].isin(choice)].sort_values(by=titles, ascending=False)[
            ['title', 'publishedAt', 'viewCount', 'likeCount', 'commentCount', 'favouriteCount']].head(5)
        fig = px.bar(samp_df, x="title", y=titles, title='bar chart ')
        fig.update_traces(marker_color='yellow')
        st.plotly_chart(fig, use_container_width=True)

    check9 = st.sidebar.checkbox('Analyse the comment section of a video')

    if check9:
        videoId = st.text_input('Input the Video Id of the video which you want to analyse the comments', 'blank')
        if videoId!='blank':
            comments = helper.get_comments(videoId,youtube)
            comment_df = pd.DataFrame(comments)
            st.subheader('The Comment Details')
            st.dataframe(comment_df)
        else:
            st.write('Input the correct videoid')

        check10=st.checkbox('Comment with highest like count or reply count')
        if check10:

            temp=st.radio('select the options',('like_count','reply_count'))
            if temp=='like_count':
                sample_df = comment_df.sort_values(by='like_count', ascending=False)[['author_name', 'comment']].iloc[0:1]
                st.write(sample_df['author_name'].to_list()[0]+' : '+sample_df['comment'].to_list()[0])
            elif temp=='reply_count':
                sample_df = comment_df.sort_values(by='reply_count', ascending=False)[['author_name', 'comment']].iloc[0:1]
                st.write(sample_df['author_name'].to_list()[0] + ' : ' + sample_df['comment'].to_list()[0])

        check12=st.checkbox('Sentiment Analysis')
        if check12:
            classifier = pipeline('sentiment-analysis', 'bert-base-multilingual-uncased-sentiment')
            comment_df['sentiment_rating'] = comment_df['comment'].apply(lambda x: helper.sentiment(x,classifier))
            conds = [
                comment_df['sentiment_rating'] > 3,
                comment_df['sentiment_rating'] == 3,
                comment_df['sentiment_rating'] < 3,
            ]
            choices = [
                'positive comment',
                'neutral comment',
                'negative comment',
            ]
            comment_df['sentiment'] = np.select(conds, choices)
            st.dataframe(comment_df)
            temp1 = st.radio('Choose from below ', ('positive comment', 'negative comment'))
            if temp1=='positive comment':
                st.header('Word cloud of Positive sentiment comments')
                string = ''
                for sent in comment_df.loc[(comment_df.sentiment == 'positive comment')]['comment']:
                    string = string + sent

                text = string
                stopwords = STOPWORDS

                wc = WordCloud(background_color="black", stopwords=stopwords, height=600, width=400)
                wc.generate(text)
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.imshow(wc, interpolation = 'bilinear')
                plt.axis("off")
                st.pyplot(fig)
            elif temp1=='negative comment':
                st.header('Word cloud of Negative sentiment comments')
                string = ''
                for sent in comment_df.loc[(comment_df.sentiment == 'negative comment')]['comment']:
                    string = string + sent

                text = string
                stopwords = STOPWORDS

                wc = WordCloud(background_color="black", stopwords=stopwords, height=600, width=400)
                wc.generate(text)
                fig, ax = plt.subplots(figsize=(12, 8))
                ax.imshow(wc, interpolation='bilinear')
                plt.axis("off")
                st.pyplot(fig)



elif user_menu=='Analysis and Download Video Transcript':
    st.write('IN DEVELOPMENT')
    videoID = st.text_input('Video Id', 'Enter the video id')
    if videoID=='Enter the video id':
        st.write('enter the id')
    else:
        YouTubeTranscriptApi.get_transcript(videoID)
        transcript = YouTubeTranscriptApi.get_transcript(videoID)
        df = pd.DataFrame(transcript)
        st.dataframe(df)
        result = ""
        for i in transcript:
            result += ' ' + i['text']
        # print(result)
        text_contents = result
        st.text(text_contents)
        st.write('Download Summarized text')

















