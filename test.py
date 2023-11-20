import streamlit as st
import pandas as pd
import xlsxwriter
from io import BytesIO

st.write("test")
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False,encoding='utf-8').encode('utf-8')

def advent_calendar_func(df):
    df=df.loc[:,~(df.columns.str.contains('Unnamed:'))]
    df=df[~(df.Module=='Totale')]
    pivot=df.pivot_table(index=['Campaign','User ID','User Name','User Surname'],columns='Module',values='Points',aggfunc='sum',margins=True,margins_name='Total').sort_values('Total',ascending=False).fillna(0)
    return pivot,df
def to_excel(pivot,df):
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    df.to_excel(workbook,sheet_name='Details')
    pivot.to_excel(workbook,sheet_name='Summary')
    workbook.close()
    return output


tab1, tab2, tab3 = st.tabs(["SOl", "[2023] Advent calendar", "[STARS]Insurance"])
with tab1:
    uploaded_file=st.file_uploader('Choose a file',key='sol')
    try:
        if uploaded_file is not None:
            df=pd.read_excel(uploaded_file, sheet_name='Matrix')
            tab1.write(df)
            csv = convert_df(df)
    except Exception as e:
        tab1.write(e)

    
    


    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='large_df.csv',
        mime='text/csv',
        key='sol'
    )

with tab2:
    uploaded_advent_file=st.file_uploader('Choose a file',key='advent_calendar')
    try:
        if uploaded_file is not None:
            df=pd.read_excel(uploaded_advent_file, sheet_name='Campaigns',skiprows=3,skipfooter=5)
            tab1.write(df)
            pivot,df=advent_calendar_func(df)
            tab2.write(df)
            tab2.write(pivot),
            out=to_excel(pivot,df)
        
    except Exception as e:
        tab2.write(e)



    st.download_button(
        label="Download data as CSV",
        data=out.get_value(),
        file_name='large_df.xlsx',
        mime='application/vnd.ms-excel',key='advent_calendar'
    )
