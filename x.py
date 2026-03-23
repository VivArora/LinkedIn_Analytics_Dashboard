import pandas as pd
import streamlit as st


# DEFINE VARIABLES

benchmark_data = {
    "Type content":["Video", "Text"],
    "B_Weergaven_LI":[355, 300],
    "B_Avg CTR_ALT":[0.0805, 0.0805],
    "B_engagement rate_LI":[0.06, 0.045]
}

df_bench = pd.DataFrame(benchmark_data)


# DEFINE FUNCTIONS
# reads raw data and 
def load_raw(file):
    try:
        df = pd.read_excel(file, 1, header=1)
        df.drop(columns=["Link plaatsen","Weergaven.1", "Soort bijdrage", "Campagnenaam", "Geplaatst door", "Begindatum van campagne", "Einddatum van campagne", "Doelgroep", "Weergaven buiten site"], inplace=True)
        df["Aangemaakt"] = pd.to_datetime(df["Aangemaakt"],  format="%m/%d/%Y")
        df["Type content"] = df["Type content"].fillna("Text")
        df["Category"] = "Enter Category"
        df = df[["Titel bijdrage", "Type content", "Category", "Weergaven", "Doorklikfrequentie (CTR)", "Interactiepercentage", "Aangemaakt"]]

        return df
    
    except Exception as e:
        return st.error(e)
    
        
def transform_silver(df):
    try:
        df_math = df.merge(df_bench, on="Type content", how="left")
        df_math["Weergaven_result"] = df_math["Weergaven"]/df_math["B_Weergaven_LI"]
        df_math["CTR_result"] = df_math["Doorklikfrequentie (CTR)"]/df_math["B_Avg CTR_ALT"]
        df_math["NTR_result"] = df_math["Interactiepercentage"]/df_math["B_engagement rate_LI"]
        df_math["post_score"] = round(((0.33*df_math["Weergaven_result"]) + (0.33*df_math["NTR_result"]) + (0.33*df_math["CTR_result"])), 2)

        st.session_state.df_calc = df_math[["Titel bijdrage", "Aangemaakt", "Type content", "Category", "Weergaven_result", "CTR_result","NTR_result","post_score"]]

        return st.session_state.df_calc
    except Exception as e:
        return st.error(e)

def calc_gold_metrics(df, df2):
    try:
        total_views = df["Weergaven"].sum()
        avg_CTR = df["Doorklikfrequentie (CTR)"].mean()
        avg_NTR = df["Interactiepercentage"].mean()
        avg_score = df2["post_score"].median()

        met1, met2, met3, met4 = st.columns(4)

        with met1:
            st.metric(label='Total views', value=total_views)
        with met2:
            st.metric(label='Avg CTR', value=round(avg_CTR, 2))
        with met3:
            st.metric(label='Avg NTR', value=round(avg_NTR, 2))
        with met4:
            st.metric(label='Median post score', value=round(avg_score, 2))
    except Exception as e:
        st.error(e)


def main():
    st.title("SDG LinkedIn Dashboard")

    uploaded_file = st.file_uploader(label="Add linkedin analytics file")

    if uploaded_file is not None:
        df_upload = load_raw(uploaded_file)

        if df_upload is not None:

            with st.expander(label="", expanded=st.session_state.expander_open):
                df_edited = st.data_editor(df_upload, hide_index=True,)

                if st.button("Submit"):
                    st.session_state.df_main = df_edited
                    st.session_state.expander_open = False
                    st.success("loaded")
                    st.rerun()

        
        if st.session_state.df_main is not None: 
            transform_silver(st.session_state.df_main)

        if st.session_state.df_main is not None:
            calc_gold_metrics(st.session_state.df_main, st.session_state.df_calc )

        

        
        

# MAIN PAGE
st.set_page_config(page_title="Linkedin Dashboard", layout="wide")

# load df_main into session state
if "df_main" not in st.session_state:
    st.session_state.df_main = None

if "expander_open" not in st.session_state:
    st.session_state.expander_open = True

if "df_calc" not in st.session_state:
    st.session_state.df_calc = None


main()