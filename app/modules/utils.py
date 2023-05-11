import os
import pandas as pd
import streamlit as st
import pdfplumber

from modules.chatbot import Chatbot
from modules.embedder import Embedder
from langchain.callbacks import get_openai_callback

from PIL import Image

class Utilities:

    @staticmethod
    def load_api_key():
        """
        Loads the OpenAI API key from the .env file or 
        from the user's input and returns it
        """
        image = Image.open('./logo.png')
        st.sidebar.image(image, width=130)

        if os.path.exists(".env") and os.environ.get("OPENAI_API_KEY") is not None:
            user_api_key = os.environ["OPENAI_API_KEY"]
            #st.sidebar.success("API key loaded from .env", icon="🚀")
        else:
            user_api_key = st.sidebar.text_input(
                label="#### Your OpenAI API key 👇", placeholder="Paste your openAI API key, sk-", type="password"
            )
            if user_api_key:
                st.sidebar.success("API key loaded", icon="🚀")

        return user_api_key
    
    @staticmethod
    def handle_upload():
        """
        Handles the file upload and displays the uploaded file
        """
        uploaded_file = st.sidebar.file_uploader("upload", type=["csv", "pdf", "txt"], label_visibility="collapsed")
        # print(uploaded_file)

        if uploaded_file is not None:

            def show_csv_file(uploaded_file):
                file_container = st.expander("Context:")
                uploaded_file.seek(0)
                shows = pd.read_csv(uploaded_file)
                file_container.write(shows)

            def show_pdf_file(uploaded_file):
                file_container = st.expander("Your PDF file :")
                with pdfplumber.open(uploaded_file) as pdf:
                    pdf_text = ""
                    for page in pdf.pages:
                        pdf_text += page.extract_text() + "\n\n"
                file_container.write(pdf_text)
            
            def show_txt_file(uploaded_file):
                file_container = st.expander("Your TXT file :")
                file_container.write(uploaded_file)
            
            def get_file_extension(uploaded_file):
                return os.path.splitext(uploaded_file)[1].lower()
            
            file_extension = get_file_extension(uploaded_file.name)

            # Show the contents of the file based on its extension
            if file_extension == ".csv" :
                show_csv_file(uploaded_file)
            elif file_extension== ".pdf" : 
                show_pdf_file(uploaded_file)
            elif file_extension== ".pdf" : 
                show_txt_file(uploaded_file)

        else:
            st.sidebar.info(
                "👆 Upload your file context to get started"
            )
            st.session_state["reset_chat"] = True

        #print(uploaded_file)
        return uploaded_file

    @staticmethod
    def setup_chatbot(uploaded_file, model, temperature,context
                      ):
        """
        Sets up the chatbot with the uploaded file, model, and temperature
        """
        embeds = Embedder()

        with st.spinner("Processing..."):
            uploaded_file.seek(0)
            file = uploaded_file.read()
            # Get the document embeddings for the uploaded file
            vectors = embeds.getDocEmbeds(file, uploaded_file.name)

            # Create a Chatbot instance with the specified model and temperature
            chatbot = Chatbot(model, temperature,vectors,context)
        st.session_state["ready"] = True

        return chatbot

    def count_tokens_agent(agent, query):
        """
        Count the tokens used by the Context Agent
        """
        with get_openai_callback() as cb:
            result = agent(query)
            st.write(f'Spent a total of {cb.total_tokens} tokens')

        return result
    
