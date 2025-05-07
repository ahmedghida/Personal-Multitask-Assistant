import streamlit as st
from utils import main_chain

st.set_page_config(page_title="MultiTask Assistant")
st.title("🤖 Personal MultiTask Assistant")

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Type your request here...")

if user_input:
    # Store user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Process response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = main_chain.invoke(user_input)
            except Exception as e:
                response = "⚠️ Sorry, an error occurred while processing your request."
                print(e)
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
