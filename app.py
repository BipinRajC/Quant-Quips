import streamlit as st

st.set_page_config(page_title="QuantQuips", page_icon="chart_with_upwards_trend", layout='wide')

st.title("QuantQuips")
st.write("Welcome to the home page of QuantQuips Description to go here.")

column1 , column2  = st.columns(2)

with column1:
    with column1:
            st.header("another picture")
            
           

    with column2:
   
            st.header("a picture")
            st.image("assets/infographic.jpeg",width=400)
            st.link_button(label="Info", url="/Infographics")

