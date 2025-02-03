from asset_historical import AssetHistorical
import streamlit as st
import altair as alt

class PageRenderer():
    @staticmethod
    @st.cache_data
    def returns_page(ticker, interval):
        if ticker != "":
            asset = AssetHistorical(ticker, interval)
            component = ComponentRenderer(asset)

            for return_type in ["C-C", "H-L", "O-C"]:
                component.returns_card(return_type)
        else:
            st.write("No data to display")

class ComponentRenderer():
    def __init__(self, asset: AssetHistorical):
        self.asset = asset

    def returns_card(self, return_type):
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

        start_date, end_date = self.asset.date_range()
        start_date = start_date.strftime("%d %b %Y")
        end_date = end_date.strftime("%d %b %Y")

        container = st.container(border=False)
        with container:
            returns_table = self.asset.returns(return_type)
            prob_table = self.asset.probabilities(return_type)
            var_table = self.asset.variance(return_type)
            summary_table = self.asset.summary(return_type)

            returns_chart = alt.Chart(returns_table).mark_bar().encode(
                x=alt.X("Range:N", title="Range", sort=returns_table.index),
                y=alt.Y("Count:Q", title="Frequency"),
            ).properties(
                title=f"{self.asset.get_name()} ({start_date} - {end_date})",
                height=400
            ).configure_title(
                anchor='middle'
            ).configure_bar(
                color=color
            )

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
