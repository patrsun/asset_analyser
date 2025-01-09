import streamlit as st
import altair as alt
from components.asset import Asset
from typing import Literal

class DataCard():
    """
    UI component class to display data analysis graphs and tables
    """
    def __init__(self, asset: Asset):
        self.asset = asset
   
    def render(self, return_type: Literal["C-C", "H-L", "O-C"]):
        asset = self.asset

        title = ""
        match return_type:
            case "C-C":
                title = "Close to Close (Adj) Distribution of Returns"
                color = '#5386E4'
            case "H-L":
                title = "High to Low Distribution of Returns"
                color = '#EF476F'
            case "O-C":
                title = "Open to Close Distribution of Returns"
                color = '#FFD166'


        container = st.container(border=False)
        with container:
            returns_table = asset.returns_table(return_type)
            prob_table = asset.prob_table(return_type)
            returns_chart = alt.Chart(returns_table).mark_bar().encode(
                x=alt.X("Range:N", title="Range", sort=returns_table.index),
                y=alt.Y("Count:Q", title="Frequency"),
            ).properties(
                title=asset.name,
                height=400
            ).configure_title(
                anchor='middle'
            ).configure_bar(
                color=color
            )

            var_table = asset.var_table(return_type)
            summary_table = asset.summary_stats(return_type)

            st.subheader(title)

            col1, col2 = st.columns(2, border=True)
            with col1:
                st.dataframe(returns_table, use_container_width=True)
                st.dataframe(summary_table, use_container_width=True)

            with col2:
                st.altair_chart(returns_chart, use_container_width=True)
                st.dataframe(prob_table, use_container_width=True)
                st.dataframe(var_table, use_container_width=True, hide_index=True)

        return container
