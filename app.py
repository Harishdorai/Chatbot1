import streamlit as st
from openai import OpenAI

# Page configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="💬",
    layout="centered"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #ffffff;  /* White main background */
    }
    .title-box {
        background-color: #d0f0d0;  /* Light green background for title box */
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 30px;
        text-align: center;
    }
    .title-text {
        color: #000080;  /* Navy blue color */
        font-weight: bold;
        font-size: 36px;
        margin: 0;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
    }
    .chat-container {
        margin-bottom: 20px;
    }
    .user-bubble {
        background-color: #e1f5fe;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        display: inline-block;
        max-width: 80%;
        margin-left: auto;
        float: right;
        clear: both;
    }
    .bot-bubble {
        background-color: #f0f0f0;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        display: inline-block;
        max-width: 80%;
        margin-right: auto;
        float: left;
        clear: both;
    }
    .api-input-container {
        max-width: 600px;
        margin: 0 auto;
        padding: 20px;
        background-color: #f9f9f9;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

if 'api_key_entered' not in st.session_state:
    st.session_state.api_key_entered = False

if 'temp_user_input' not in st.session_state:
    st.session_state.temp_user_input = ""

# App title with box
st.markdown("<div class='title-box'><p class='title-text'>YOUR QUERIES</p></div>", unsafe_allow_html=True)

# Function to interact with OpenAI API
def get_openai_response(prompt, api_key):
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Function to set API key
def set_api_key():
    temp_key = st.session_state.get("temp_api_key", "")
    if temp_key.strip():
        st.session_state.api_key = temp_key
        st.session_state.api_key_entered = True
        # Test connection
        try:
            # Quick test to verify the API key works
            client = OpenAI(api_key=temp_key)
            client.models.list()
            st.session_state.api_key_valid = True
        except Exception:
            st.session_state.api_key_valid = False

# Function to handle message submission
def handle_message_submit():
    user_input = st.session_state.get("message_input", "")
    if user_input and st.session_state.api_key:
        # Store the user's message
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Get response from the API
        ai_response = get_openai_response(user_input, st.session_state.api_key)
        
        # Store the AI's response
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        # This is automatically cleared by Streamlit since we're using key= parameter

# Two-phase interface: API key entry, then chat
if not st.session_state.api_key_entered:
    # Show API key input screen
    st.markdown("<div class='api-input-container'>", unsafe_allow_html=True)
    st.subheader("Enter your OpenAI API Key to start chatting")
    st.text_input("OpenAI API Key", 
                 type="password", 
                 key="temp_api_key", 
                 placeholder="sk-...")
    st.button("Submit API Key", on_click=set_api_key)
    st.markdown("</div>", unsafe_allow_html=True)
    
else:
    # Check if the key is valid
    if not st.session_state.get("api_key_valid", False):
        st.error("Invalid API key. Please try again.")
        st.session_state.api_key_entered = False
        st.rerun()
        
    # Show the chat interface
    # Display chat history
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"<div class='user-bubble'>{message['content']}</div><div style='clear:both'></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bot-bubble'>{message['content']}</div><div style='clear:both'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Input for new messages
    st.text_input("Type your message here...", key="message_input", on_change=handle_message_submit)
    
    # Option to reset API key
    if st.sidebar.button("Change API Key"):
        st.session_state.api_key_entered = False
        st.session_state.api_key = ""
        st.rerun()