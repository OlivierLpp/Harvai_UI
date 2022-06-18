from re import A
from tkinter.tix import LabelEntry
from urllib import request
import streamlit as st
from streamlit_chat import message
import requests
import os
from decouple import config
import time

ARTICLES = None

st.set_page_config(
    #initial_sidebar_state="collapsed",
    layout ="centered",
    page_title="HarvAI - V1 - Test",
    page_icon=":robot:"
)

#load local env variable if not on heroku else load heroku env variable
is_prod = os.environ.get('IS_HEROKU', None)

if is_prod:
    API_URL = os.environ['API_URL']
    API_TOKEN = os.environ['API_TOKEN']
else:
    API_URL = config('API_URL')
    API_TOKEN = config('API_TOKEN')

#headers = {"Authorization": f"Bearer {API_TOKEN}"}

st.markdown("<h1 style='text-align: center; color: white;'>HarvAI</h1>", unsafe_allow_html=True)


# ------------ Parameters------------


st.sidebar.markdown(f"""
    ## PARAMETERS
    """)

retriever =st.sidebar.radio('Select a Retriever :', ('KNN', 'BM25', 'DPR', 'Embedding'),index=3)
nb_articles = st.sidebar.slider('Select a number of articles :', 1, 10, 4)
reader_generator = st.sidebar.radio('Select a Q/A generator :', ('Camembert', 'Other'))
st.sidebar.markdown("[Github](https://github.com/MarcusLZ/harvai)")


# ------------ Chat Box ------------


if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

def get_text():
    input_text = st.text_input("You: ","", key="input")
    return input_text

user_input = get_text()

if user_input:

    output = requests.get("http://127.0.0.1:8000/answer", params={'question': user_input, 'retriever' : retriever, 'article_number' : nb_articles})
    print(output)
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output.json()['answer'])
    ARTICLES = output.json()['parsed_context']

    print(retriever, nb_articles, reader_generator)
    print(output.json()['answer'], output.json()['parsed_context'])


if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], key=str(i))


# ------------ Articles Expander ------------


def hightlight(article, user_input):
    new = ""
    input = user_input.lower().split()

    for word in article.split():
        if word.lower() in input:
            new = new + " <mark style='background-color: DodgerBlue;'>" + word + "</mark>"
        else:
            new = new + ' ' + word
    return new

with st.expander("See Articles Returned"):

    if ARTICLES is not None:
        for article in ARTICLES:
            st.markdown("""---""")
            st.markdown(hightlight(article, user_input), unsafe_allow_html=True)
