import streamlit as st

st.set_page_config(page_title="QuantQuips", page_icon="chart_with_upwards_trend", layout='wide')

st.title("QuantQuips")
st.write("Welcome to the home page of QuantQuips Description to go here.")

column1 , column2  = st.columns(2)

with column1:
    with column1:
        st.header("A cat")
        st.image("https://static.streamlit.io/examples/cat.jpg")

    with column2:
        st.header("A dog")
        st.image("https://static.streamlit.io/examples/dog.jpg")

