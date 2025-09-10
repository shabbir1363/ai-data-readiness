import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Page setup
st.set_page_config(page_title="Advanced Data Analytics", layout="wide")

# Show centered logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.png", use_container_width=True)

st.title("Advanced Data Analytics Dashboard")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    # Load data
    df = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully")

    # Show raw data preview
    st.subheader("Raw Data Preview")
    st.dataframe(df.head())

    # Show data types and sample values (convert samples to strings to avoid errors)
    st.subheader("Data Types and Sample Values")
    col_types = pd.DataFrame({
        "Column": df.columns,
        "Data Type": df.dtypes,
        "Sample Values": [str(df[col].dropna().unique()[:5]) for col in df.columns]
    })
    st.dataframe(col_types)

    # Convert columns to numeric where possible (non-convertible become NaN)
    df_numeric = df.copy()
    for col in df.columns:
        df_numeric[col] = pd.to_numeric(df[col], errors='coerce')

    # Summary statistics on original df (including categoricals)
    st.subheader("Summary Statistics (Original Data)")
    st.write(df.describe(include='all'))

    # Summary statistics on cleaned numeric data
    st.subheader("Summary Statistics (Numeric Columns Only)")
    st.write(df_numeric.describe())

    # Correlation heatmap on numeric columns only
    numeric_cols = df_numeric.select_dtypes(include=np.number).columns
    st.subheader("Correlation Heatmap")
    if len(numeric_cols) >= 2:
        corr = df_numeric[numeric_cols].corr()
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)
    else:
        st.info("Not enough numeric columns for correlation heatmap.")

    # Interactive Plotly scatter plot for numeric columns
    st.subheader("Interactive Scatter Plot")
    if len(numeric_cols) >= 2:
        x_axis = st.selectbox("Select X-axis", options=numeric_cols)
        y_axis = st.selectbox("Select Y-axis", options=numeric_cols, index=1)
        fig2 = px.scatter(df_numeric, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("Please upload data with at least two numeric columns after cleaning.")

    # Download cleaned numeric data
    st.subheader("Download Cleaned Numeric Data")
    csv = df_numeric.to_csv(index=False)
    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="cleaned_numeric_data.csv",
        mime="text/csv",
    )

else:
    st.info("Please upload a CSV file to get started.")