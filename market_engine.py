
import sqlite3
import pandas as pd


def classify_sentiment(rating):
    """Classify a review using its star rating."""
    if pd.isna(rating):
        return "Neutral"
    elif rating >= 4:
        return "Positive"
    elif rating == 3:
        return "Neutral"
    else:
        return "Negative"


def clean_reviews(df):
    """Clean review text and classify sentiment."""
    df = df.copy()

    df["review_text"] = (
        df["review_text"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    df["review_date"] = pd.to_datetime(
        df["review_date"], errors="coerce"
    )

    df["sentiment"] = df["rating"].apply(
        classify_sentiment
    )

    return df


def save_to_database(df, db_path="competitor_intelligence_clean.db"):
    """Save only new reviews to the SQLite database."""

    if df.empty:
        print("No reviews to save.")
        return 0

    df = df.copy()
    df = df.drop_duplicates(
        subset=["app_id", "review_id"],
        keep="first"
    )

    df["app_id"] = df["app_id"].astype(str)
    df["review_id"] = df["review_id"].astype(str)

    with sqlite3.connect(db_path) as connection:
        existing = pd.read_sql_query(
            "SELECT app_id, review_id FROM reviews",
            connection
        )

        existing_keys = set(
            zip(
                existing["app_id"].astype(str),
                existing["review_id"].astype(str)
            )
        )

        mask = [
            (app_id, review_id) not in existing_keys
            for app_id, review_id in zip(
                df["app_id"], df["review_id"]
            )
        ]

        new_reviews = df.loc[mask]

        if not new_reviews.empty:
            new_reviews.to_sql(
                "reviews",
                connection,
                if_exists="append",
                index=False
            )

    print(f"New unique reviews saved: {len(new_reviews)}")
    return len(new_reviews)
    



def create_excel_report(
    df, file_path="competitor_intelligence_report.xlsx"
):
    """Create a multi-sheet Excel report."""
    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        df.to_excel(
            writer, sheet_name="All Reviews", index=False
        )

        sentiment_summary = (
            df.groupby(["app_name", "sentiment"])
            .size()
            .reset_index(name="review_count")
        )
        sentiment_summary.to_excel(
            writer, sheet_name="Sentiment Summary", index=False
        )

        rating_summary = (
            df.groupby("app_name")["rating"]
            .agg(["count", "mean"])
            .reset_index()
        )
        rating_summary.columns = [
            "app_name", "review_count", "average_rating"
        ]
        rating_summary.to_excel(
            writer, sheet_name="Rating Summary", index=False
        )

    return file_path
