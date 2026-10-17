import streamlit as st
from google_play_scraper import search, reviews, Sort
import pandas as pd
all_reviews = []

from market_ai import analyze_market_gaps

if "reviews_df" not in st.session_state:
    st.session_state["reviews_df"] = None



from market_engine import (
    clean_reviews,
    save_to_database,
    create_excel_report
)


st.set_page_config(
    page_title="Market Intelligence Tool",
    page_icon="📊",
    layout="wide"
)

st.title("Market Intelligence & Competitor Scraping Tool")
st.write("Gemini key loaded:", bool(st.secrets.get("GEMINI_API_KEY")))
st.write("Discover, select, and compare competing mobile applications.")

st.subheader("Step 1: Discover Competitors")

keyword = st.text_input(
    "Search for apps or a market niche",
    placeholder="Example: food delivery"
)

if st.button("Search Apps"):
    if not keyword.strip():
        st.warning("Please enter an app name or keyword.")
    else:
        try:
            with st.spinner("Searching Google Play..."):
                results = search(
                    keyword.strip(),
                    lang="en",
                    country="us",
                    n_hits=10
                )

            st.session_state["search_results"] = results
            st.session_state["selected_apps"] = []

        except Exception as error:
            st.error("Search failed. Check your internet connection.")
            st.caption(f"Technical details: {error}")

if "search_results" in st.session_state:
    results = st.session_state["search_results"]

    if not results:
        st.info("No apps found. Try another keyword.")
    else:
        st.subheader("Step 2: Select Competitors")
        st.write("Select between 2 and 4 apps to analyze.")

        selected_apps = []

        for i, app in enumerate(results):
            app_id = app.get("appId", str(i))
            title = app.get("title", "Unknown app")

            with st.container(border=True):
                col1, col2 = st.columns([1, 5])

                with col1:
                    icon_url = app.get("icon")
                    if icon_url:
                        st.image(icon_url, width=80)

                with col2:
                    st.write(f"**{title}**")
                    st.write(
                        f"Developer: {app.get('developer', 'Unknown')}"
                    )
                    st.write(
                        f"Rating: {app.get('score', 'Not available')}"
                    )

                    if st.checkbox(
                        f"Select {title}",
                        key=f"select_{app_id}"
                    ):
                        selected_apps.append(app)

        st.write(f"Selected competitors: {len(selected_apps)}")

        if st.button("Confirm Competitors"):
            if len(selected_apps) < 2:
                st.warning("Please select at least 2 apps.")
            elif len(selected_apps) > 4:
                st.warning("Please select no more than 4 apps.")
            else:
                st.session_state["selected_apps"] = selected_apps
                st.success("Competitors selected successfully!")

                for app in selected_apps:
                    st.write(
                        f"- {app.get('title')} "
                        f"({app.get('appId')})"
                    )

                st.info(
                    "Next: collect customer reviews for these apps."
                )

st.divider()
st.subheader("Step 3: Collect Customer Reviews")

selected_apps = st.session_state.get("selected_apps", [])

if selected_apps:
    review_limit = st.selectbox(
        "Reviews per app",
        [150, 200, 300],
        index=0
    )

    if st.button("Collect Reviews"):
        all_reviews = []

        progress = st.progress(0)
        status = st.empty()

        for index, app in enumerate(selected_apps):
            app_id = app.get("appId")

            status.write(
                f"Collecting reviews for {app.get('title')}..."
            )

            try:
                result, _ = reviews(
                    app_id,
                    lang="en",
                    country="us",
                    sort=Sort.NEWEST,
                    count=review_limit
                )

                for review in result:
                    all_reviews.append({
                        "app_id": app_id,
                        "app_name": app.get("title"),
                        "review_id": review.get("reviewId"),
                        "rating": review.get("score"),
                        "review_text": review.get("content"),
                        "review_date": review.get("at")
                    })

            except Exception as error:
                st.warning(
                    f"Could not collect reviews for "
                    f"{app.get('title')}: {error}"
                )

            progress.progress((index + 1) / len(selected_apps))

       


if all_reviews:
    df = pd.DataFrame(all_reviews)
    df = clean_reviews(df)
    st.session_state["reviews_df"] = df

    save_to_database(df)
    report_path = create_excel_report(df)

elif st.session_state["reviews_df"] is not None:
    df = st.session_state["reviews_df"]

else:
    df = None


if df is not None:
    st.success("Review collection completed!")

    st.write(f"Total reviews collected: {len(df)}")
    st.write("Reviews per app:")
    st.write(df["app_name"].value_counts())
    st.dataframe(df, use_container_width=True)

    csv_data = df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "Download Reviews as CSV",
        data=csv_data,
        file_name="competitor_reviews.csv",
        mime="text/csv"
    )

    report_path = create_excel_report(df)

    with open(report_path, "rb") as excel_file:
        st.download_button(
            "Download Excel Report",
            data=excel_file,
            file_name="competitor_intelligence_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.subheader("AI Market Gap Analysis")

    if st.button("Analyze Market Gaps with AI"):
        with st.spinner("Analyzing customer complaints..."):
            analysis = analyze_market_gaps(df)

        st.markdown(analysis)

else:
    st.info("Please search for apps and confirm your competitors first.")
