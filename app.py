"""
Flipkart Products - Interactive Dashboard
Run: streamlit run app.py
"""
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Flipkart Products Analysis", layout="wide")

@st.cache_data
def load_data():
    return pd.read_csv("data/flipkart_clean.csv")

df = load_data()

st.title("🛒 Flipkart Products Analysis")
st.markdown("Pricing, discount, and category analysis of ~10,000 Flipkart product listings.")

# ---------------- Sidebar filters ----------------
st.sidebar.header("Filters")
categories = st.sidebar.multiselect("Category", sorted(df[df["category"] != "Unknown"]["category"].unique()))
price_range = st.sidebar.slider(
    "Retail Price (₹)",
    int(df["retail_price"].min()),
    int(df["retail_price"].quantile(0.99)),
    (int(df["retail_price"].min()), int(df["retail_price"].quantile(0.99))),
)

filtered = df.copy()
if categories:
    filtered = filtered[filtered["category"].isin(categories)]
filtered = filtered[
    (filtered["retail_price"] >= price_range[0]) & (filtered["retail_price"] <= price_range[1])
]

# ---------------- KPIs ----------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Products", f"{len(filtered):,}")
col2.metric("Avg Retail Price", f"₹{int(filtered['retail_price'].mean())}")
col3.metric("Avg Discount %", f"{filtered['discount_pct'].mean():.1f}%")
col4.metric("Unique Categories", filtered["category"].nunique())

st.divider()

c1, c2 = st.columns(2)

with c1:
    st.subheader("Top 10 Categories by Product Count")
    cat_counts = filtered[filtered["category"] != "Unknown"]["category"].value_counts().head(10)
    fig = px.bar(x=cat_counts.values, y=cat_counts.index, orientation="h",
                 labels={"x": "Products", "y": "Category"})
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Avg Discount % by Category (Top 10)")
    cat_filtered = filtered[filtered["category"] != "Unknown"]
    disc_by_cat = cat_filtered.groupby("category")["discount_pct"].mean().sort_values(ascending=False).head(10)
    fig = px.bar(x=disc_by_cat.values, y=disc_by_cat.index, orientation="h",
                 labels={"x": "Avg Discount %", "y": "Category"})
    st.plotly_chart(fig, use_container_width=True)

c3, c4 = st.columns(2)

with c3:
    st.subheader("Price vs Discount %")
    sample = filtered.sample(min(3000, len(filtered)))
    fig = px.scatter(sample, x="retail_price", y="discount_pct", opacity=0.5)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    st.subheader("Price Distribution")
    fig = px.histogram(filtered, x="retail_price", nbins=40)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Top 10 Brands by Product Count")
brand_counts = filtered[filtered["brand"] != "Unknown"]["brand"].value_counts().head(10)
fig = px.bar(x=brand_counts.index, y=brand_counts.values, labels={"x": "Brand", "y": "Products"})
st.plotly_chart(fig, use_container_width=True)

st.divider()
st.caption("Data source: Flipkart Products dataset | Built by Abhishek Kumar")
