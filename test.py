import streamlit as st
import pandas as pd

st.write("test")
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False,encoding='utf-8').encode('utf-8')
tab1, tab2, tab3 = st.tabs(["SOl", "[2023] Advent calendar", "[STARS]Insurance"])
with tab1:
    uploaded_file=tab1.file_uploader('Choose a file')
    try:
        df=pd.read_excel(uploaded_file, sheet_name='Matrix')
    except Exception as e:
        st.write(e)

    df.columns=df.columns.str.strip()
    tab1.write(df)
    csv = convert_df(df)

    tab1.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='large_df.csv',
        mime='text/csv',
    )

with tab2:
    uploaded_advent_file=tab2.file_uploader('Choose a file')
    try:
        df=pd.read_excel(uploaded_advent_file, sheet_name='Campaigns',skiprows=3,skipfooter=5)
    except Exception as e:
        st.write(e)

    df.columns=df.columns.str.strip()
    tab2.write(df)


    csv = convert_df(df)

    tab2.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='large_df.csv',
        mime='text/csv',
    )
