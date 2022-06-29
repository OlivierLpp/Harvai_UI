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
START = None
END = None

st.set_page_config(
    #initial_sidebar_state="collapsed",
    layout ="wide",
    page_title="HarvAI",
    page_icon=":desktop_computer:"
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


# ------------ Side Bar------------

from PIL import Image
image = Image.open('images/robot_reading.png')
st.sidebar.image(image)
st.sidebar.markdown("<div><h1 style='text-align: center; color: white;'>HarvAI</h1></div>", unsafe_allow_html=True)
st.sidebar.markdown("Un chatbot intelligent qui répond directement à toutes vos questions juridiques sur le code de la route.")
st.sidebar.markdown("<br>Pour commencer : <ol><li> Ecrivez une question dans l'espace alloué et appuyez sur entrer</li> <li>Vous pouvez modifier les paramètres via les commandes ci dessous</li></ol>",unsafe_allow_html=True)

# ------------ Parameters------------

st.sidebar.markdown(f"""
    ## Paramètres :
    """)

retriever =st.sidebar.radio('Retriever :', ('KNN', 'BM25', 'DPR', 'Embedding'),index=0)
nb_articles = st.sidebar.slider("Nombre d'articles retournés:", 1, 10, 4)
#reader_generator = st.sidebar.radio('Selectionner le reader :', ('Camembert', 'Other'))
st.sidebar.markdown("[Github](https://github.com/MarcusLZ/harvai)")


# ------------ Chat Box ------------


if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

def get_text():
    input_text = st.text_input("Question : ","", key="input")
    return input_text

col1, col_separateur, col2= st.columns((5,1,5))

with col1 :
    user_input = get_text()

    if user_input:

        output = requests.get("http://127.0.0.1:8000/answer", params={'question': user_input, 'retriever' : retriever, 'article_number' : nb_articles})
        print(output)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output.json()['answer']['answer'])


        ARTICLES = output.json()["parsed_context"]
        ARTICLES_REFERENCE = output.json()["article_reference"]
        START = output.json()['answer']['start']
        END = output.json()['answer']['end']

        print(ARTICLES_REFERENCE)
        print(output.json()['answer']['answer'], output.json()['parsed_context'])


    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))


# ------------ Articles Expander ------------


def hightlight(articles, start, end, reference):
    new = ""
    for number, article in enumerate(articles):
        new = new + "<b>" + str(reference[number]) + ":" + "</b> <br>"
        for count, word in enumerate(list(article)):
            if count == int(start) and start > 0:
                new = new + " <mark style='background-color: DodgerBlue;'>" + word
            elif count == int(end) and end > 0:
                new = new + word + "</mark>"
            else:
                new = new + word
        new = new + "<p></p>"
        start = start - len(article)
        end = end - len(article)
    return new

with col2:
    st.markdown("Articles retournés :")
    if ARTICLES is not None:
        st.markdown(hightlight(ARTICLES, START, END, ARTICLES_REFERENCE), unsafe_allow_html=True)
