import streamlit as st
import pandas as pd
import xlsxwriter
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


def liste_stock_df_convert(uploaded_file,pwd):
    passwd = pwd

    decrypted_workbook = io.BytesIO()
    with open(uploaded_file, 'rb') as file:
        office_file = msoffcrypto.OfficeFile(file)
        office_file.load_key(password=passwd)
        office_file.decrypt(decrypted_workbook)
    df=pd.read_excel(decrypted_workbook ,sheet_name='Liste Stocks',skiprows=1)
    df=df[df['Ptf / Libre']==0]
    df=df[(df['Reg']=="BDX")|(df['Reg']=="LYN")|(df['Reg']=="MTZ")|(df['Reg']=="PRS")|(df['Reg']=="RNS")]

    return df

def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv(index=False,encoding='utf-8').encode('utf-8')

def advent_calendar_func(df):
    df=df.loc[:,~(df.columns.str.contains('Unnamed:'))]
    df=df[~(df.Module=='Totale')]
    df=df[['User ID','User Name','User Surname','Module','Campaign','Points']]
    df.drop_duplicates(inplace=True)
    pivot=df.pivot_table(index=['Campaign','User ID','User Name','User Surname'],columns='Module',values='Points',aggfunc='sum',margins=True,margins_name='Total').sort_values('Total',ascending=False).fillna(0)
    #pivot['User ID']=pivot['User ID'].astype(str)
    return pivot,df
def to_excel(pivot,df):
    output = BytesIO()
    #workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer,sheet_name='Details',index=False)
        pivot.to_excel(writer,sheet_name='Summary')
        #writer.save()
    return output


tab1, tab2, tab3 = st.tabs(["SOl", "[2023] Advent calendar", "Opel Stock"])
with tab1:
    uploaded_file=tab1.file_uploader('Choose a file',key='sol')
    try:
        if uploaded_file is not None:
            df=pd.read_excel(uploaded_file, sheet_name='Matrix')
            tab1.write(df)

            csv = convert_df(df)
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


with tab3:
    uploaded_stock_file=tab3.file_uploader('Choose a file',key='stock')
    try:
        if uploaded_stock_file is not None:
            pwd=tab3.text_input(
                "Password for file", type="password", key="password_stock")
            df=liste_stock_df_convert(uploaded_stock_file,pwd)
            
            tab3.write('Details')
            tab3.write(df)
            tab3.download_button(
                label="Download data as xlsx",
                data=df,
                file_name='Stock_Opel_df.xlsx',
                mime='application/vnd.ms-excel',key='stock_download'
        )
        
    except Exception as e:
        tab3.write(e)




