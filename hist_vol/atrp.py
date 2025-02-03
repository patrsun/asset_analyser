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

    col1, col2 = st.columns(2, border=True)
    col3, col4 = st.columns(2, border=True)

    def dataframe(df):
        return st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

    with col1:
        st.subheader("Daily ATRP")
        dataframe(daily.atrp_table())
    with col2:
        st.subheader("Weekly ATRP")
        dataframe(weekly.atrp_table())
    with col3:
        st.subheader("Monthly ATRP")
        dataframe(monthly.atrp_table())
    with col4:
        st.subheader("Quarterly ATRP")
        dataframe(quarterly.atrp_table())

render_page(ticker)
