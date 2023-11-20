import streamlit as st
import pandas as pd

st.write("test")
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False,encoding='utf-8').encode('utf-8')
tab1, tab2, tab3 = st.tabs(["SOl", "[2023] Advent calendar", "[STARS]Insurance"])
with tab1:
    uploaded_file=st.file_uploader('Choose a file',key='sol')
    try:
        df=pd.read_excel(uploaded_file, sheet_name='Matrix')
    except Exception as e:
        st.write(e)

    df.columns=df.columns.str.strip()
    st.write(df)
    csv = convert_df(df)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='large_df.csv',
        mime='text/csv',
    )

with st:
    uploaded_advent_file=st.file_uploader('Choose a file',key='advent_calendar')
    try:
        df=pd.read_excel(uploaded_advent_file, sheet_name='Campaigns',skiprows=3,skipfooter=5)
    except Exception as e:
        st.write(e)

    df.columns=df.columns.str.strip()
    st.write(df)


    csv = convert_df(df)

    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='large_df.csv',
        mime='text/csv',
    )
