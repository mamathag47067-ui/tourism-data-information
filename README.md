# Tourism Data Visualization Dashboard

An interactive tourism dashboard built with **Python, Streamlit, Pandas, and Plotly** using the `most-visited-countries-2024.csv` dataset.

## Features

- Sidebar filters for countries, arrival metrics, ranking size, and ranking metric
- Summary cards that respond to the selected filters
- Country-wise tourist arrival ranking bar chart
- Comparison chart for selected arrival metrics
- Scatter plot comparing two selected metrics
- Histogram showing the distribution of tourist arrivals
- Optional filtered data table
- All visualizations use the same filtered dataset

## Files

- `app.py` — Streamlit dashboard application
- `most-visited-countries-2024.csv` — dataset
- `requirements.txt` — Python dependencies

## Run locally

1. Install Python 3.10 or newer.
2. Open Command Prompt or terminal in this project folder.
3. Install packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the dashboard:
dashboard link :https://tourism-data-information-jmauaacigoyuqfzbyh4cec.streamlit.app/

   ```bash
   streamlit run app.py
   ```

5. Streamlit will show a local URL, usually `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository, for example `Tourism-Data-Visualization`.
2. Upload `app.py`, `requirements.txt`, and `most-visited-countries-2024.csv` to the repository root.
3. Visit https://share.streamlit.io/ and sign in with GitHub.
4. Choose **Create app**, select your repository and branch, and set the main file path to `app.py`.
5. Click **Deploy**.

## Dataset note

The dataset includes predicted tourist arrivals for 2024, arrival figures for 2022 and 2023, and a World Bank arrivals field with a separate data-year column. The World Bank field can refer to different years for different countries, so do not treat it as a single-year comparison without checking `World Bank Data Year`.

## GitHub repository suggestion

Repository name: `Tourism-Data-Visualization`
