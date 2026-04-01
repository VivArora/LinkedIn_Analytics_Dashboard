"""
- refactor code into functions
- API key integration so data doesnt have to be uploaded
- titles
- improved layout and flow
- update variable and metric names
- add helpers to each section
- update categ section
    - add just title, content type, post date
- create content type and category json config file
- 
- add followers as main metric
- add date filters
    - month
        - week
    - category
    - type

STEPS
- upload document
- read data
- add new rows to master file
- for new rows, show category and type columns to be added
- once values are submitted, remove editor from view
    - if nr of rows in new_rows_data_editor = 0, dont show editor
- start main dashboard
- filter for month and weeks
- show metrics
    - based on selected filter
        - total views, median(?) performance relative to benchmark, nr of followers gains
            - for all, have relative gain from pervious period
- detailed breakdown
    - some sort of plot per post 
    - per content type
        - per category
            - top 3 latest posts and post score
            - 
    
"""


import pandas as pd
import streamlit as st
#from streamlit_dynamic_filters import DynamicFilters

# DEFINE VARIABLES

benchmark_data = {
    "Type content":["Video", "Text", "Image", "Multi image", "Link", "Poll"],
    "B_Weergaven_LI":[355, 300, 315, 490, 235, 340],
    "B_Avg CTR_ALT":[0.0805, 0.0805, 0.0805,0.0805,0.0805,0.0805],
    "B_engagement rate_LI":[0.06, 0.045, 0.053, 0.0645, 0.0325, 0.042]
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
        avg_score = df2["post_score"].mean()

        met1, met2, met3, met4 = st.columns(4)

        with met1:
            st.metric(label='Total views', value=total_views, help="Total post view over export period")
        with met2:
            st.metric(label='Avg CTR (%)', value=round(avg_CTR*100, 2), help="Average CTR of posts over export period")
        with met3:
            st.metric(label='Avg Engagement (%)', value=round(avg_NTR*100, 2), help="Average engagement rate of posts over export period")
        with met4:
            st.metric(label='Avg Post Score (x)', value=round(avg_score, 2), help="The post score indicates the performance of posts relative to linkedin benchmarks (thus a post score of 2 means the post performs 2x better than the benchmark)")
    except Exception as e:
        st.error(e)

def gold_categ_BC(df):
    try:
        df_categ_res = df.groupby("Category")["post_score"].mean()
        st.write("The post score is a weighted average of the views, CTR and engagement rate of each post. The score indicates the performance of a post relative to a standard benchmark. Thus, a post score of 2 means that the post performs 2x better than the benchmark")
        st.bar_chart(df_categ_res)
    except Exception as e:
        st.error(e)

def main():
    st.title("SDG LinkedIn Dashboard")
    st.write("This is a platform to upload an export of linkedin analytics for month end performance reporting")
    
    st.subheader("Instructions")
    st.write("1) Upload the linkedin export file")
    
    

    uploaded_file = st.file_uploader(label="Add linkedin analytics file")

    if uploaded_file is not None:
        df_upload = load_raw(uploaded_file)

        st.write("2) In the drop down menu below, enter the category values (and edit the content type if needed) per post")

        with st.expander(label="Manually add values to columns **`Type Content`** and **`Categories`** to categorize posts by clicking the cell and typing", expanded=st.session_state.expander_open):
            df_edited = st.data_editor(df_upload, hide_index=True,)
            st.write("3) Press submit when all values are added to view results")
            if st.button("Submit"):
                st.session_state.df_main = df_edited
                st.session_state.expander_open = False
                st.rerun()

        
        if st.session_state.df_main is not None: 
            transform_silver(st.session_state.df_main)

        if st.session_state.df_calc is not None:
            st.title("Main results")
            calc_gold_metrics(st.session_state.df_main, st.session_state.df_calc)

            st.subheader("Average post-score per Category")
            gold_categ_BC(st.session_state.df_calc)

            with st.expander(label="Table view of results (graph view WIP)"):
                st.subheader("Benchmark breakdown")
                st.dataframe(st.session_state.df_calc)

                st.subheader("Post Data")
                st.dataframe(st.session_state.df_main)

            
        

        
        

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