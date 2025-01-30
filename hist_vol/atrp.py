from components.asset import Asset
import streamlit as st

ticker = st.session_state["ticker"]

@st.cache_data
def render_page(ticker):
    daily = Asset(ticker, interval = "1d")
    weekly = Asset(ticker, interval = "5d")
    monthly = Asset(ticker, interval = "1mo")
    quarterly = Asset(ticker, interval = "3mo")

    st.title(daily.name)

    col1, col2, col3, col4 = st.columns(4, border=True)

    with col1:
        st.subheader("Daily ATRP")
        st.dataframe(daily.atrp(), use_container_width=True)
    with col2:
        st.subheader("Weekly ATRP")
        st.dataframe(weekly.atrp(), use_container_width=True)
    with col3:
        st.subheader("Monthly ATRP")
        st.dataframe(monthly.atrp(), use_container_width=True)
    with col4:
        st.subheader("Quarterly ATRP")
        st.dataframe(quarterly.atrp(), use_container_width=True)

if ticker != "":
    try:
        render_page(ticker)
    except: 
        st.write("Invalid ticker symbol")
else:
    st.write("No data to display")
