# Market Intelligence & Competitor Scraping Tool

## Project Overview
The Market Intelligence & Competitor Scraping Tool is a Python-based application designed to collect and analyze Google Play reviews from competing mobile applications.

It helps users understand customer satisfaction, identify recurring complaints, discover unmet user needs, and generate data-driven recommendations.

## Key Features
- Search for mobile applications on Google Play.
- Select multiple competitor applications for comparison.
- Collect and clean user reviews.
- Classify reviews as Positive, Neutral, or Negative.
- Store review data in an SQLite database.
- Generate downloadable Excel reports.
- Visualize competitor insights using interactive charts.
- Use Gemini AI to analyze customer complaints and identify potential market gaps.

## Technologies Used
- Python
- Streamlit
- Pandas
- SQLite
- Plotly
- Google Play Scraper
- Google Gemini API
- Excel report generation

## Project Structure
- `app.py` — Streamlit user interface.
- `market_engine.py` — Review processing and database operations.
- `market_ai.py` — AI-powered market analysis.
- `requirements.txt` — Project dependencies.
- `competitor_intelligence_clean.db` — Cleaned review database.

## How to Run Locally

1. Clone or download this repository.
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure your Gemini API key using Streamlit secrets.

4. Run the application:

   ```bash
   python -m streamlit run app.py
   ```

## Security
Never upload API keys, passwords, or private credentials to GitHub. Store API keys securely using Streamlit secrets.

## Future Improvements
- Expand competitor coverage.
- Improve sentiment analysis accuracy.
- Add more advanced competitor comparison metrics.
- Deploy the application to Streamlit Community Cloud.

## Author
Developed as a market intelligence and data analysis project.
