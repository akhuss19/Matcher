import streamlit as st
import pandas as pd
from match_agent import run_matching

st.title("📚 Strive Higher — Volunteer Matching Agent")

participants_file = st.file_uploader("Upload Participants Excel File", type="xlsx")
volunteers_file = st.file_uploader("Upload Volunteers Excel File", type="xlsx")

if participants_file and volunteers_file:
    try:
        # Run matching using match_agent.py
        result = run_matching(participants_file, volunteers_file)

        st.success("🎉 Matching complete!")
        st.dataframe(result)

        st.download_button(
            "Download Matches",
            data=result.to_excel(index=False),
            file_name="matches.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except KeyError as e:
        st.error(f"❌ {e}")
