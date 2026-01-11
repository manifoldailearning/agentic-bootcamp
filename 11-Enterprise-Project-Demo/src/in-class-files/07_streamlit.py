import streamlit as st

st.set_page_config(
    page_title="My First Streamlit App",
    page_icon="🎉",
    layout = "centered"
)

st.title("Welcome to my first Streamlit App")
st.write("This is a simple app that I built with Streamlit")

name = st.text_input("Enter your name")

if st.button("Submit"):
    st.success(f"Hello {name}!, Welcome to my first Streamlit App")

else:
    st.warning("Please enter your name")

if st.checkbox("Show me the code"):
    st.code("import streamlit as st")

color = st.radio("Choose your favorite color", ["Blue", "Red", "Green"])
if color:
    st.write(f"You selected {color}")

# sidebar

st.sidebar.header("Controls")
temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
max_tokens = st.sidebar.selectbox("Max Tokens", [128, 256, 512, 1024, 2048])

prompt = st.text_area("Enter your prompt", height=200)

if st.button("Run Agent"):
    st.info("Running Agent...")
    st.write(f"Temperature: {temperature}")
    st.write(f"Max Tokens: {max_tokens}")
    st.write(f"Prompt: {prompt}")
    st.success("Agent ran successfully")
