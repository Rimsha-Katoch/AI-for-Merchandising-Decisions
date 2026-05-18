import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("Product Visibility Optimization Dashboard")
st.sidebar.header("⚙ Simulation Controls")

factor = st.sidebar.slider(
    "Increase Impression Factor",
    min_value=0.8,
    max_value=2.0,
    value=1.2,
    step=0.1
)

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    df["ctr"] = df["clicks"]/df["impressions"]
    df["cvr"] = df["orders"]/df["clicks"]
    df["revenue"] = df["orders"] * df["price"]
    df["profit"] = df["revenue"] * df["margin"]

    st.write("### Dataset Preview")
    st.dataframe(df.head())

    st.write("### Key Metrics")

    # KPI
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Revenue", f"{df["revenue"].sum():,.0f}")
    col2.metric("Total Profit", f"{df["profit"].sum():,.0f}")
    col3.metric("Average CTR", f"{df["ctr"].mean():.2%}")
    col4.metric("Average CVR", f"{df["cvr"].mean():.2%}")

    st.write("## 📈 Profit by Category")

    category_summary = df.groupby("category")["profit"].sum().reset_index()

    # Create Plot
    fig, ax = plt.subplots()
    sns.barplot(
        data=category_summary,
        x="category",
        y="profit",
        ax=ax
    )

    ax.set_title("Total Profit by Category")
    # labels on bar
    for i, row in category_summary.iterrows():
        ax.text(i, row["profit"]+1000, round(row["profit"], 0), ha="center")

    st.pyplot(fig)

    st.write("## 🌍 Location + Category Analysis")

    location_summary = (df.groupby(["location", "category"])[
                        ["revenue", "profit"]].sum().reset_index())

    st.dataframe(location_summary)

    st.write("## 🔍 Relationship Between Visibility and Sales")

    correlation = df["impressions"].corr(df["orders"])
    st.write(f"### Correlation: {round(correlation, 3)}")

    st.info(
        "A moderate positive correlation suggests that higher visibility generally leads to more orders, "
        "although other factors such as conversion rate and product quality also influence sales.")

    fig2, ax2 = plt.subplots()
    ax2.scatter(df["impressions"], df["orders"])
    ax2.set_xlabel("Impressions")
    ax2.set_ylabel("Orders")
    ax2.set_title("Impressions vs Orders")
    st.pyplot(fig2)

    st.write("## 🔮 Revenue Simulation")

    df["new_impressions"] = df["impressions"] * factor
    df["expected_clicks"] = df["new_impressions"] * df["ctr"]

    df["demand"] = (df["expected_clicks"] * df["cvr"])
    df["expected_orders"] = pd.concat(
        [df["demand"], df["stock"]], axis=1).min(axis=1)
    df["expected_revenue"] = (df["expected_orders"] * df["price"])
    # Compare Revenue
    original_revenue = df["revenue"].sum()

    expected_revenue = df["expected_revenue"].sum()

    increase_percent = (
        (expected_revenue - original_revenue) / original_revenue) * 100

    # Display Results
    col5, col6, col7 = st.columns(3)

    col5.metric("Original Revenue", f"{original_revenue:,.0f}")

    col6.metric("Expected Revenue", f"{expected_revenue:,.0f}")

    col7.metric("Revenue Change %", f"{increase_percent:.2f}%")

    st.write("## 📈 Revenue vs Visibility Change")

    factors = [0.8, 1.0, 1.2, 1.5]
    results = {}
    for f in factors:
        new_impressions = df["impressions"] * f

        expected_clicks = (
            new_impressions * df["ctr"]
        )

        demand = (
            expected_clicks * df["cvr"]
        )

        final_orders = pd.concat(
            [demand, df["stock"]],
            axis=1
        ).min(axis=1)

        expected_revenue_loop = (
            final_orders * df["price"]
        ).sum()

        results[f] = expected_revenue_loop

    fig3, ax3 = plt.subplots()

    ax3.plot(
        list(results.keys()),
        list(results.values()),
        marker='o'
    )
    ax3.set_xlabel("Impression Factor")
    ax3.set_ylabel("Expected Revenue")
    ax3.set_title("Revenue vs Visibility Change")

    ax3.grid()
    st.pyplot(fig3)


else:
    st.info("Please upload a CSV file.")
