import streamlit as st
import requests

API = "http://localhost:8000"


st.set_page_config(
    page_title="Authentication Service",
    page_icon="🔒",
    layout="centered",
)

user_name = st.text_input("Enter your username")
password = st.text_input("Enter your password", type="password")

params = {
    "username": user_name,
    "password": password
}
headers = {
    "accept": "application/json"
}

if st.button("Login"):
    response = requests.post(f"{API}/login", params=params, headers=headers, data='')
    st.write(response.json())
    if response.status_code == 200:
        st.session_state.token = response.json()["access_token"]
        st.success("Login successful")
    else:
        st.error("Login failed")

st.divider()

if st.session_state.token:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

st.write(f"User Info: {st.session_state.token}")