# Asset Analyser - Historical Volatility Calcuator 
https://assetanalyser.streamlit.app/

A Streamlit app for analysing volatility of financial assets (equities, bonds ETFs, currencies, etc.) to help me learn about trading.
Currently only has functionality for distribution of returns analysis of historical price data. 

Future plans:
- Average True Range Percentage
- Implied Volatility

Some screenshots:
<img width="1414" alt="Screenshot 2025-07-02 at 20 59 47" src="https://github.com/user-attachments/assets/0c9618ec-852a-44fe-8370-1e370cf99c63" />
<img width="1416" alt="Screenshot 2025-07-02 at 20 59 38" src="https://github.com/user-attachments/assets/d69f0b28-2249-4767-96f3-12adf0028c58" />
<img width="1419" alt="Screenshot 2025-07-02 at 20 59 28" src="https://github.com/user-attachments/assets/3d7969b5-0f48-4170-96c0-eef7fcc77084" />
<img width="1413" alt="Screenshot 2025-07-02 at 20 59 12" src="https://github.com/user-attachments/assets/064b845d-aa9e-42f1-adac-f7e9ee66cba4" />

To run:

Clone the repository, then:
```
pip install streamlit
pip install -r requirements.txt
```
```
streamlit run app.py
```

Enter whatever a valid ticker symbol on the left and then you will have your data!
