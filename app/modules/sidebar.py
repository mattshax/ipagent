import streamlit as st
import os

class Sidebar:

    MODEL_OPTIONS = ["gpt-3.5-turbo", "gpt-4"]
    TEMPERATURE_MIN_VALUE = 0.0
    TEMPERATURE_MAX_VALUE = 1.0
    TEMPERATURE_DEFAULT_VALUE = 0.0
    TEMPERATURE_STEP = 0.01

    @staticmethod
    def about():
        about = st.sidebar.expander("🧠 About Robby ")
        sections = [
            "#### Robby is an AI chatbot with a conversational memory, designed to allow users to discuss their data in a more intuitive way. 📄",
            "#### It uses large language models to provide users with natural language interactions about user data content. 🌐",
            "#### Works with CSV and PDF files, more soon...",
            "#### Powered by [Langchain](https://github.com/hwchase17/langchain), [OpenAI](https://platform.openai.com/docs/models/gpt-3-5) and [Streamlit](https://github.com/streamlit/streamlit) ⚡",
            "#### Source code: [yvann-hub/Robby-chatbot](https://github.com/yvann-hub/Robby-chatbot)",
        ]
        for section in sections:
            about.write(section)

    @staticmethod
    def reset_chat_button():
        if st.button("Reset chat"):
            st.session_state["reset_chat"] = True
        st.session_state.setdefault("reset_chat", False)

    def model_selector(self):
        model = st.selectbox(label="Model", options=self.MODEL_OPTIONS)
        st.session_state["model"] = model

    def temperature_slider(self):
        temperature = st.slider(
            label="Temperature",
            min_value=self.TEMPERATURE_MIN_VALUE,
            max_value=self.TEMPERATURE_MAX_VALUE,
            value=self.TEMPERATURE_DEFAULT_VALUE,
            step=self.TEMPERATURE_STEP,
        )
        st.session_state["temperature"] = temperature
        
    def csv_agent_button(self, uploaded_file):
        st.session_state.setdefault("show_csv_agent", False)
        
        if uploaded_file and os.path.splitext(uploaded_file.name)[1].lower() == ".csv":
            if st.button("Context Agent"):
                st.session_state["show_csv_agent"] = not st.session_state["show_csv_agent"]

    def show_options(self, uploaded_file,authenticator):
        with st.sidebar.expander("🛠️ Settings", expanded=False):

            self.reset_chat_button()
            self.csv_agent_button(uploaded_file)
            self.model_selector()
            self.temperature_slider()
            st.session_state.setdefault("model", self.MODEL_OPTIONS[0])
            st.session_state.setdefault("temperature", self.TEMPERATURE_DEFAULT_VALUE)
        
        with st.sidebar:
            if authenticator != None:
                authenticator.logout('Logout', 'main', key='unique_key')

    