"""
Flipkart Products - Data Cleaning Script
Run this first: python clean_data.py
Output: data/flipkart_clean.csv
"""
import pandas as pd
import re

RAW_PATH = "data/flipkart.csv"
CLEAN_PATH = "data/flipkart_clean.csv"


def extract_top_category(tree):
    """product_category_tree looks like ["Clothing >> Women's Clothing >> ..."] -> pull first level.
    If there's no '>>' hierarchy (just the product name), it's not a real category -> Unknown."""
    if pd.isna(tree) or ">>" not in str(tree):
        return "Unknown"
    match = re.search(r'\["?(.*?)>>', tree)
    if match:
        return match.group(1).strip().strip('"')
    return "Unknown"


def clean_flipkart(path=RAW_PATH):
    df = pd.read_csv(path)

    # 1. Drop rows that are entirely broken (CSV parsing artifacts from the source mirror)
    df = df.dropna(subset=["product_name", "retail_price"]).copy()

    # 2. Drop columns not useful for pricing/category analysis
    df.drop(columns=["crawl_timestamp", "image", "product_url", "pid"], inplace=True, errors="ignore")

    # 3. Extract top-level category from product_category_tree
    df["category"] = df["product_category_tree"].apply(extract_top_category)

    # 4. Numeric price columns
    df["retail_price"] = pd.to_numeric(df["retail_price"], errors="coerce")
    df["discounted_price"] = pd.to_numeric(df["discounted_price"], errors="coerce")
    df = df.dropna(subset=["retail_price", "discounted_price"])

    # 5. Discount %
    df["discount_pct"] = ((df["retail_price"] - df["discounted_price"]) / df["retail_price"] * 100).round(1)
    df["discount_pct"] = df["discount_pct"].clip(lower=0)

    # 6. Clean rating: "No rating available" -> NaN, else float
    for col in ["product_rating", "overall_rating"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 7. Fill missing brand
    df["brand"] = df["brand"].fillna("Unknown")

    # 8. Remove duplicate products
    df.drop_duplicates(subset=["uniq_id"], inplace=True)

    df.reset_index(drop=True, inplace=True)
    return df


if __name__ == "__main__":
    df = clean_flipkart()
    df.to_csv(CLEAN_PATH, index=False)
    print(f"Cleaned data saved to {CLEAN_PATH}")
    print(f"Shape: {df.shape}")
    print(df["category"].value_counts().head(10))
