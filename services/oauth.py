import requests
import streamlit as st
import urllib.parse
import secrets
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLIENT_ID = st.secrets["oauth_client_id"]
CLIENT_SECRET = st.secrets["inoreader_key"]
REDIRECT_URI = st.secrets["redirect_uri"]
AUTHORIZATION_URL = st.secrets["authorization_url"]
TOKEN_URL = st.secrets["token_url"]
SCOPE = "read"

def get_authorization_url():
    # Use the already-stored oauth_state
    logger.info("Getting auth url")
    state = st.session_state.get("oauth_state")
    logger.info(state)
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPE,
        "state": state,
    }
    return f"{AUTHORIZATION_URL}?{urllib.parse.urlencode(params)}"

def exchange_code_for_token(auth_code):
    logger.info("Exchanging code for token")
    data = {
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    logger.info(data)
    response = requests.post(TOKEN_URL, data=data)
    logger.info(response)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def fetch_inoreader_data():
    headers = {
        "Authorization": f"Bearer {st.session_state.access_token}",
    }
    response = requests.get("https://www.inoreader.com/reader/api/0/user-info", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching data from Inoreader: {response.text}")
        return None
