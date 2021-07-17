from youtubesearchpython import VideosSearch
from youtube_transcript_api import YouTubeTranscriptApi
import re
import pandas as pd
import numpy as np
from wordcloud import WordCloud
from PIL import Image
import streamlit as st
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import xlsxwriter

@st.cache
def search_videos(video_thema, total_pages = 2, results_limit = 10):	

	videosSearch = VideosSearch(video_thema, limit = results_limit)
	

	#Combine all the results
	all_results = []

	for i in range(0, total_pages):
	  new_query = videosSearch.result()["result"]
	  all_results = all_results + new_query
	  videosSearch.next()


	# Then we will iterate through the video result and extract the video_id
	video_ids = []
	for video in all_results:
	  video_ids.append(video["id"])

	return video_ids


@st.cache
def get_transcriptions(video_ids, language = "it"):

	#Extract the transcriptions of each video in a list
	transcriptions = []
	for id_video in video_ids:
	  try:
	    transcription = YouTubeTranscriptApi.get_transcript(id_video, languages= [language])
	    transcriptions.append(transcription)

	  #To catch the exception if the video doesn't have subtitles 
	  except Exception:
	      pass

	return transcriptions



def get_text_transcriptions(transcriptions):
	#Now we will extract only the text of each transcription
	only_text = []
	for transcription in transcriptions:
	  for trans in transcription:
	    text = trans["text"]
	    only_text.append(text)

	return only_text



def clean_and_count(only_text, min_lon = 3):
	#Now we will count the words of each text, and we will remove numbers and symbols
	count_words = {}

	for text in only_text:
	  #first we remove the \n
	  text = re.sub("\n", ' ', text)
	  for word in text.split():

	    #We only keep the letters
	    clean_word = re.sub(r'[^A-Za-z]', '', word)
	    
	    #All to lowercase
	    clean_word = clean_word.lower()
	    if clean_word != '' and len(clean_word) >= min_lon:
	      if clean_word in count_words:
	        count_words[clean_word] += 1
	      else:
	        count_words[clean_word] = 1

	return count_words



def transform_dataframe(count_words, base_string = "https://context.reverso.net/traduccion/italiano-espanol/"):
	df = pd.DataFrame.from_dict(count_words, orient = "index")
	df.columns = ["Count"]
	df = df.sort_values(by = "Count", ascending = False).reset_index()
	df.columns = ["Word", "Count"]

	#Convert into percentage
	df["percentage"] = (df["Count"]/sum(df["Count"])) * 100


	#And now we will calculate the cummulative percentage
	df["Cumulative_percentage"] = df["percentage"].cumsum()


	#We will use the examples of context.reverso.net, combining the path with the word we are looking for:
	df["Examples"] = base_string + df["Word"]

	return df


def make_clickable(val):
    return '<a href="{}">{}</a>'.format(val,val)


def make_hyperlink(value):
    url = "https://context.reverso.net/traduccion/italiano-espanol/"
    return '=HYPERLINK("%s", "%s")' % (url.format(value), value)


def word_cloud(count_words, mask_path = "Italy.png"):

	mask = np.array(Image.open(mask_path))

	# Generate a word cloud image from frequencies
	wordcloud = WordCloud(background_color="white", mask= mask,
	                      contour_width=3, contour_color='steelblue').generate_from_frequencies(count_words)

	# Display the generated image:
	plt.figure(figsize=(16,8))
	plt.imshow(wordcloud, interpolation="bilinear")
	plt.axis("off")
	plt.show()


def df_to_html(dataframe):
	df = dataframe

	#We can also export this to show it in a webpage:
	html_info = (
	    df.style
	    .format({'Examples': make_clickable})
	    .render()
	)

	return html_info


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="words_list.xlsx">Download the list of words in excel</a>' # decode b'abc' => abc
