# 🎈 Blank app template

A simple Streamlit app template for you to modify!

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://blank-app-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

# of Structure of app
# vendor_risk scoring package has separate modules for each type of score (financial_stability.py, past_performance.py, foreign_labor.py, and federal_contract.py)
# utils.py module includes common utilities for csv handling to avoid code repetition
# score calculation pipeline is added with (score_calculator.py) to handle orchestration by involving each scoring function and combining their results