import streamlit as st
import pandas as pd
import re
from dateutil import parser
from io import BytesIO

# ---------------- Helper functions ----------------
def split_list(cell):
    if pd.isna(cell):
        return []
    items = re.split(r"[;,/]+", str(cell))
    return [i.strip().lower() for i in items if i.strip()]

def normalize_time(t):
    try:
        dt = parser.parse(t)
        return dt.strftime("%H:%M")
    except:
        return str(t).strip().lower()

def normalize_times_list(tokens):
    return sorted(list({normalize_time(t) for t in tokens}))

def overlap(list1, list2):
    return any(i in list2 for i in list1)

def compute_score(child, vol):
    score = 0
    if overlap(child["_days"], vol["_days"]): score += 3
    if overlap(child["_times"], vol["_times"]): score += 3
    if overlap(child["_langs"], vol["_langs"]): score += 4
    return score

# ---------------- Streamlit UI ----------------
st.title("📚 Strive Higher — Volunteer Matching Agent")

participants_file = st.file_uploader("Upload Participants Excel File", type=["xlsx"])
volunteers_file = st.file_uploader("Upload Volunteers Excel File", type=["xlsx"])

if participants_file and volunteers_file:
    # Load uploaded Excel files
    p = pd.read_excel(participants_file)
    v = pd.read_excel(volunteers_file)

    # Column names (adjust these if needed)
    P_NAME = "Student's Full Name"
    P_DAYS = "Day Availability  (one day will be assigned)-  please select at least two days"
    P_TIMES = "Please check off the times that you & your child would be available  (a specific time will be determined)-  please select at least two times"

    V_DAYS = "Day(s) Available-  Please select at least two days"
    V_TIMES = "Time Availability (Sessions are 30min- 1 hour long)- Please select at least two times"
    V_LANG = "Do you speak another language? If so, please include it below."

    # ---------------- Preprocess participants ----------------
    if P_DAYS in p.columns and P_TIMES in p.columns:
        p["_days"] = p[P_DAYS].apply(split_list)
        p["_times"] = p[P_TIMES].apply(lambda x: normalize_times_list(split_list(x)))
    else:
        st.error("Participants file is missing required columns.")
        st.stop()

    p["_langs"] = [[] for _ in range(len(p))]  # Optional

    # ---------------- Preprocess volunteers ----------------
    if V_DAYS in v.columns and V_TIMES in v.columns:
        v["_days"] = v[V_DAYS].apply(split_list)
        v["_times"] = v[V_TIMES].apply(lambda x: normalize_times_list(split_list(x)))
    else:
        st.error("Volunteers file is missing required columns.")
        st.stop()

    v["_langs"] = v[V_LANG].apply(split_list) if V_LANG in v.columns else [[] for _ in range(len(v))]

    # ---------------- Compute matches ----------------
    matches = []
    for _, child in p.iterrows():
        best_score = -1
        best_vol = None

        for _, vol in v.iterrows():
            score = compute_score(child, vol)
            if score > best_score:
                best_score = score
                best_vol = vol[V_NAME]

        matches.append({
            "Child": child[P_NAME],
            "Best Volunteer": best_vol,
            "Match Score": best_score
        })

    result = pd.DataFrame(matches)
    st.success("Matching complete!")
    st.dataframe(result)

    # ---------------- Download button ----------------
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Matches")
        processed_data = output.getvalue()
        return processed_data

    st.download_button(
        label="Download Matches",
        data=to_excel(result),
        file_name="matches.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Please upload both Participants and Volunteers Excel files to start matching.")