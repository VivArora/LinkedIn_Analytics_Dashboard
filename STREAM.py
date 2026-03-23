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



st.set_page_config(page_title="Linkedin Dashboard", layout="wide")
## TYPE CONTENT AND ADD FOR CATEGORY




if "dfx" not in st.session_state:
    st.session_state.dfx = None

li_file = st.file_uploader(label="add linkedin analytics file")

if li_file:
    #st.success("file loaded")
    try:
        #st.write("starting load")
        df = pd.read_excel(li_file, 1, header=1)
        df.drop(columns=["Link plaatsen","Weergaven.1", "Soort bijdrage", "Campagnenaam", "Geplaatst door", "Begindatum van campagne", "Einddatum van campagne", "Doelgroep", "Weergaven buiten site"], inplace=True)
        df["Aangemaakt"] = pd.to_datetime(df["Aangemaakt"],  format="%m/%d/%Y")
        df["Type content"] = df["Type content"].fillna("Text")
        df["Category"] = "Enter Category"
        df = df[["Titel bijdrage", "Type content", "Category", "Weergaven", "Doorklikfrequentie (CTR)", "Interactiepercentage", "Aangemaakt"]]
        #st.success("df loaded")
        with st.expander(label="Enter Type content and categorize each post", ):
            # FEATURE
            ## read the date range and create filters for month and week
            # [["Aangemaakt","Titel bijdrage", "Type content", "Category"]]
            edited_df = st.data_editor(df, hide_index=True, )
        
        if st.button("Submit changes"):
            st.session_state.dfx = edited_df
            st.success("Data loaded")


        benchmark_data = {
            "Type content":["Video", "Text"],
            "B_Weergaven_LI":[355, 300],
            "B_Avg CTR_ALT":[0.0805, 0.0805],
            "B_engagement rate_LI":[0.06, 0.045]
        }

        df_bench = pd.DataFrame(benchmark_data)
        df_test = None

        if st.session_state.dfx is not None:
            df_test = st.session_state.dfx.merge(df_bench, on="Type content", how="left")

        
        try:
            df_test["Weergaven_result"] = df_test["Weergaven"]/df_test["B_Weergaven_LI"]
            df_test["CTR_result"] = df_test["Doorklikfrequentie (CTR)"]/df_test["B_Avg CTR_ALT"]
            df_test["NTR_result"] = df_test["Interactiepercentage"]/df_test["B_engagement rate_LI"]
            df_test["post_score"] = round(((0.33*df_test["Weergaven_result"]) + (0.33*df_test["NTR_result"]) + (0.33*df_test["CTR_result"])), 2)

            df_results = df_test[["Titel bijdrage", "Aangemaakt", "Type content", "Category", "Weergaven_result", "CTR_result","NTR_result","post_score"]]

            total_views = st.session_state.dfx["Weergaven"].sum()
            avg_CTR = st.session_state.dfx["Doorklikfrequentie (CTR)"].mean()
            avg_NTR = st.session_state.dfx["Interactiepercentage"].mean()
            avg_score = df_results["post_score"].median()


            met1, met2, met3, met4 = st.columns(4)

            with met1:
                st.metric(label='Total views', value=total_views)
            with met2:
                st.metric(label='Avg CTR', value=round(avg_CTR, 2))
            with met3:
                st.metric(label='Avg NTR', value=round(avg_NTR, 2))
            with met4:
                st.metric(label='Median post score', value=round(avg_score, 2))


            df_categ_res = df_results.groupby("Category")["post_score"].mean()
            st.bar_chart(df_categ_res)
        except Exception as e:
            st.error(f'error: {e}')
        # txt_cat_rest = df_res_text.groupby(by=["Category"])["post_score"].mean()
        # st.dataframe(txt_cat_rest)
        



        # tab1, tab2 = st.columns(2)
        # with tab1:
        #     df_res_text = df_results.query("Type content == 'Text'")
        #     txt_cat_rest = df_res_text.groupby(by=["Category"])["post_score"].mean()
        #     st.dataframe(txt_cat_rest)
        # with tab2:
        #     df_res_vid = df_results.query("Type content == 'Video'")
        #     vid_cat_rest = df_res_vid.groupby(by=["Category"])["post_score"].mean()
        #     st.dataframe(vid_cat_rest)




    except Exception as e:
        st.error(f"Error: {e}")
#metrics

