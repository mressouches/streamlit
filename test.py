import streamlit as st
import pandas as pd
from io import BytesIO
import hmac
 
# =============================================================================
# GESTION DU MOT DE PASSE
# =============================================================================
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# =============================================================================
# FONCTIONS POUR L'ONGLET "SOL"
# =============================================================================

def charger_donnees(fichier_upload, nom_feuille):
    """
    Charge les données depuis un fichier Excel téléversé via Streamlit.
    """
    try:
        df = pd.read_excel(fichier_upload, sheet_name=nom_feuille)
        return df
    except Exception as e:
        st.error(f"ERREUR : Une erreur est survenue lors de la lecture du fichier Excel : {e}")
        return None

def nettoyer_et_transformer(df):
    """
    Nettoie et transforme les données du DataFrame.
    Toutes les colonnes numériques restent des nombres (int/float).
    """
    if df is None:
        return None
    
    df_clean = df.copy()

    df_clean.columns = df_clean.columns.str.strip()
    df_clean['Model'] = df_clean['Model'].astype(str).str.replace('ë', 'e')

    for col in ['disclaimer', 'disclaimer stellantis']:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype(str).str.replace("<br/>", '.', regex=False)
            df_clean[col] = df_clean[col].str.replace(r'.\*', '<br/>*', regex=True)
            df_clean[col] = df_clean[col].str.replace(r'\n\*', '<br/>*', regex=True)
            df_clean[col] = df_clean[col].str.replace(r'\.', '.<br/>', regex=True)

    for col in ['Unpublished', 'Stock', 'Highlight']:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].fillna(0).astype(int)
    
    return df_clean

def formater_pour_affichage(df):
    """
    Applique le formatage final pour l'affichage (%, €) sur les colonnes spécifiées.
    C'est la dernière étape de transformation avant l'export.
    """
    if df is None:
        return None
        
    df_formatted = df.copy()

    def _formater_valeur(valeur):
        """Fonction interne pour formater une seule valeur."""
        if pd.isna(valeur):
            return ""  # Retourne une chaîne vide pour les valeurs manquantes
        
        try:
            valeur_float = float(valeur)
            if 0 <= valeur_float <= 1:
                return f"{valeur_float:.0%}"
            else:
                return f"{valeur_float:,.0f} €".replace(",", " ")
        except (ValueError, TypeError):
            return valeur

    colonnes_a_formater = ['Default', 'Groupe 1 & 2 - Employee', 'Groupe 3 - Employee']
    for col in colonnes_a_formater:
        if col in df_formatted.columns:
            df_formatted[col] = df_formatted[col].apply(_formater_valeur)
            
    return df_formatted

def convert_df_to_csv(df):
    """Convertit le DataFrame en CSV (bytes) pour le téléchargement."""
    return df.to_csv(index=False, sep=';', encoding='cp1252').encode('cp1252')


# =============================================================================
# FONCTIONS POUR L'ONGLET "ADVENT CALENDAR"
# =============================================================================
def advent_calendar_func(df):
    df=df.loc[:,~(df.columns.str.contains('Unnamed:'))]
    df=df[~(df.Module=='Totale')]
    df=df[['User ID','User Name','User Surname','Module','Campaign','Points']]
    df.drop_duplicates(inplace=True)
    pivot=df.pivot_table(index=['Campaign','User ID','User Name','User Surname'],columns='Module',values='Points',aggfunc='sum',margins=True,margins_name='Total').sort_values('Total',ascending=False).fillna(0)
    return pivot,df

def to_excel(pivot,df=None):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        if df is not None:
            df.to_excel(writer,sheet_name='Details',index=False)
        if pivot is not None:
            pivot.to_excel(writer,sheet_name='Summary')
    return output

# =============================================================================
# APPLICATION STREAMLIT PRINCIPALE
# =============================================================================
st.title("Tools")

tab1, tab2 = st.tabs(["SOL", "Advent calendar"])

# --- ONGLET 1 : SOL ---
with tab1:
    uploaded_file = tab1.file_uploader('Choisissez un fichier Excel pour SOL', type=['xlsx', 'xls'], key='sol')
    
    if uploaded_file is not None:
        try:
            # Étape 1: Charger les données brutes
            df_brut = charger_donnees(uploaded_file, nom_feuille='Matrix')
            
            if df_brut is not None:
                tab1.markdown("### Aperçu des données brutes chargées")
                df_brut_print = df_brut.astype("string[python]").astype(object)
                tab1.dataframe(df_brut_print)

                # Étape 2: Nettoyer les données (types numériques conservés)
                df_nettoye = nettoyer_et_transformer(df_brut)
                
                # Étape 3: Formater les données pour l'affichage et l'export (nombres -> chaînes de caractères formatées)
                df_final_formate = formater_pour_affichage(df_nettoye)

                tab1.markdown("### Aperçu des données finales")
                df_final_formate_print = df_final_formate.astype("string[python]").astype(object)
                tab1.dataframe(df_final_formate_print)

                # Préparation du fichier CSV pour le téléchargement
                csv_data = convert_df_to_csv(df_final_formate)
                
                tab1.download_button(
                    label="Télécharger les données en CSV",
                    data=csv_data,
                    file_name='sol_matrix_export.csv',
                    mime='text/csv',
                    key='sol_download'
                )
        except Exception as e:
            tab1.error(f"Une erreur inattendue est survenue : {e}")

# --- ONGLET 2 : ADVENT CALENDAR ---
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
