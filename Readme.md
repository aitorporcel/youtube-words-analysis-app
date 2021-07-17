# Most common Italian words using the 80/20 principle

Simple web app that uses the Pareto principle (20% of the effort explains 80% of the results), to obtain the 1000 most used words in a language (in this case italian) from youtube videos.
This little prototype web application (https://translation-app-it.herokuapp.com/) was created using Streamlit and deployed in Heroku and:
* Performs a YouTube search.
* Gets the transcripts of the videos in the selected language.
* Generates a word count.
* Returns a word cloud along with a downloadable Excel (sorting the words by the percentage of the time they are used).
