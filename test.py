import streamlit as st
import pandas as pd
import xlsxwriter
from openpyxl import load_workbook
from io import BytesIO
import msoffcrypto
import hmac
import streamlit as st

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the passward is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# Main Streamlit app starts here
st.write("Tools")


def convert_to_percentage(value):
    try:
        # tenter de convertir la valeur en float
        value_float = float(value)
        return "{:.0%}".format(value_float)  # convertir en pourcentage et formater
    except (ValueError, TypeError):
        # si la conversion échoue (par exemple, pour les valeurs vides ou non numériques),
        # renvoyer la valeur telle quelle
        return value

def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    df.Model=df.Model.astype(str)
    df.Model=df.Model.str.replace('ë','e')

    df.disclaimer=df.disclaimer.str.replace("<br/>",'.')
    df.disclaimer=df.disclaimer.replace('.\*', '<br/>*', regex=True)
    df.disclaimer=df.disclaimer.replace('\n\*', '<br/>*', regex=True)
    df.disclaimer=df.disclaimer.replace('\.', '.<br/>', regex=True)
    try:
        #df["Highlight"] = df["Highlight"].astype(int)
        df['disclaimer stellantis']=df['disclaimer stellantis'].str.replace("<br/>",'.')
        df['disclaimer stellantis']=df['disclaimer stellantis'].replace('.\*', '<br/>*', regex=True)
        df['disclaimer stellantis']=df['disclaimer stellantis'].replace('\n\*', '<br/>*', regex=True)
    except Exception as e:
        pass


    """df['Default']=(df['Default'].astype(int)*100).astype(str)+"%"
    df['Groupe 1 & 2 - Employee']=(df['Groupe 1 & 2 - Employee'].astype(int)*100).astype(str)+"%"
    df['Groupe 3 - Employee']=(df['Groupe 3 - Employee'].astype(int)*100).astype(str)+"%"""
    df.columns=df.columns.str.strip()
    #df=df.apply(lambda x: x.str.strip() if x.dtype=="object" else x)
    df.Unpublished.fillna(0,inplace=True)
    df.Unpublished=df.Unpublished.astype(int)
    df.Stock.fillna(0,inplace=True)
    df.Stock = df.Stock.astype(int)
    df.Highlight.fillna(0,inplace=True)
    df.Highlight = df.Highlight.astype(int)
    return df.to_csv(index=False,encoding='cp1252',sep=';').encode('cp1252'),df

def advent_calendar_func(df):
    df=df.loc[:,~(df.columns.str.contains('Unnamed:'))]
    df=df[~(df.Module=='Totale')]
    df=df[['User ID','User Name','User Surname','Module','Campaign','Points']]
    df.drop_duplicates(inplace=True)
    pivot=df.pivot_table(index=['Campaign','User ID','User Name','User Surname'],columns='Module',values='Points',aggfunc='sum',margins=True,margins_name='Total').sort_values('Total',ascending=False).fillna(0)
    #pivot['User ID']=pivot['User ID'].astype(str)
    return pivot,df

def to_excel(pivot,df=None):
    output = BytesIO()
    #workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        if df is not None:
            df.to_excel(writer,sheet_name='Details',index=False)
        if pivot is not None:
            pivot.to_excel(writer,sheet_name='Summary')
        #writer.save()
    return output


tab1, tab2 = st.tabs(["SOL", "Advent calendar"])
with tab1:
    uploaded_file=tab1.file_uploader('Choose a file',key='sol')
    try:
        if uploaded_file is not None:
            df=pd.read_excel(uploaded_file, sheet_name='Matrix',converters={'Default':convert_to_percentage,'Groupe 1 & 2 - Employee':convert_to_percentage,'Groupe 3 - Employee':convert_to_percentage})
            tab1.write(df) 
            
            csv,df_transformed = convert_df(df)
            tab1.write(df_transformed)
            tab1.download_button(
            label="Download data as CSV",
            data=csv,
            file_name='large_df.csv',
            mime='text/csv',
            key='sol_download'
        )
    except Exception as e:
        tab1.write(e)

with tab2:
    uploaded_advent_file=tab2.file_uploader('Choose a file',key='advent_calendar')
    try:
        if uploaded_advent_file is not None:
            df=pd.read_excel(uploaded_advent_file, sheet_name='Campaigns',skiprows=3,skipfooter=5)
            pivot,df=advent_calendar_func(df)
            tab2.write('Details')
            tab2.write(df)

            tab2.write('Summary')
            tab2.write(pivot.reset_index())
            out=to_excel(pivot,df)
            tab2.download_button(
                label="Download data as xlsx",
                data=out,
                file_name='large_df.xlsx',
                mime='application/vnd.ms-excel',key='advent_calendar_download'
        )
        
    except Exception as e:
        tab2.write(e)
