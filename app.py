from urllib import request
import streamlit as st
from streamlit_chat import message
import requests
import os
from decouple import config
import time


st.set_page_config(
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

st.header("HarvAI - V1 - Test")
st.markdown("[Github](https://github.com/MarcusLZ/harvai)")


columns = st.columns(2)
retriever = columns[0].radio('Select a Retriever :', ('KNN', 'BM25', 'DPR', 'Embedding'))
reader_generator = columns[1].radio('Select a Q/A generator :', ('Camembert', 'Other'))


if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

def get_text():
    input_text = st.text_input("You: ","", key="input")
    return input_text


user_input = get_text()



if user_input:

    output = requests.get("http://127.0.0.1:8000/answer", params={'question': user_input, 'retriever' : retriever})

    st.session_state.past.append(user_input)
    st.session_state.generated.append(output.json()['answer'])


if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
        message(st.session_state["generated"][i], key=str(i))
