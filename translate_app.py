# -*- coding: utf-8 -*-
"""
Created on 22/06/2021

@author: Aitor
"""

import streamlit as st
from app_functions import *
import pickle
 

#Resolver esto algun dia armando una figura para mostrar
st.set_option('deprecation.showPyplotGlobalUse', False)

st.title("Most common Italian words using the 80/20 principle")
st.write("According to the Pareto Principle, 20% of the words are used in 80% of the situations. That is, by knowing 20% of the language it is possible to understand 80% of the conversation. This application allows you to obtain those words representing 80% of the conversation in specific situations (from YouTube videos).")
st.write("To use it:")
st.write("- Select the topic of interest.")
st.write("- Select your native language.")
st.write("- Select the target language.")
st.write("- Filter the shorter words (most are known as stopwords, you can play with the filter to get different results).")
st.write("- Click Search, and the app will return some general metrics, a word cloud, and a table with examples for each word.")


#video_thema = st.text_input('Write about which topic you want to learn vocabulary: ', value = 'conversazione in italiano')
video_thema = st.selectbox(label = 'What topic do you want to learn vocabulary about?: ', options = ["conversazione in italiano",
                                                                                                     "presentazione in italiano",
                                                                                                     "colloquio di lavoro"])


col1, col2, col3 = st.beta_columns(3)

from_language = col1.selectbox(label = "Select your language", options = ["Spanish"])
to_language = col2.selectbox(label = "Select the topic's language", options = ["Italian"])
min_lon = col3.number_input("Minimum word length to be considered", min_value = 0, max_value = 5, value = 4, step = 1)


dict_languages = {"Italian": "it"}

if st.button('Search'):

    #Search if the file exists for these search
    try:
        with open("transcriptions/" + video_thema, 'rb') as file:
            transcriptions = pickle.load(file)

    #Otherwise call the API
    except:
        video_ids = search_videos(video_thema, total_pages = 2, results_limit = 20)
        transcriptions = get_transcriptions(video_ids, language = dict_languages[to_language])

        #Save the new file
        with open("transcriptions/" + video_thema, 'wb') as file:
            pickle.dump(transcriptions, file)

    st.write(f"Total videos considered {len(transcriptions)}")

    only_text = get_text_transcriptions(transcriptions)

    count_words = clean_and_count(only_text, min_lon)

    df = transform_dataframe(count_words, base_string = "https://context.reverso.net/traduccion/italiano-espanol/")


    df['Examples'] = df['Examples'].apply(make_clickable)
    df_display = df[:1000].to_html(escape=False)

    total_words = df.shape[0]
    cumulative_percentage_1000 = df["Cumulative_percentage"][1000]

    st.write("\n")
    st.write(f"Total number of different words: {total_words}")
    st.write(f"Percentage of time in which the first 1,000 words are used: {cumulative_percentage_1000: .2f}%")
    st.write(f"Percentage of the first 1000 words with respect to the total number of words.: {(1000/total_words)*100: .2f}%")
    st.write("\n")

    st.subheader("Cloud of most used words: ")
    st.pyplot(word_cloud(count_words, mask_path = "Italy.png"))

    st.subheader("1000 most used words in this topic (with examples)")
    
    #To download
    df_excel = df
    df_excel["Examples"] = df_excel["Word"].apply(make_hyperlink)
    st.markdown(get_table_download_link(df_excel), unsafe_allow_html=True)

    st.write(df_display, unsafe_allow_html=True)

