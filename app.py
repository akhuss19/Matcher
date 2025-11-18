import streamlit as st
import pandas as pd
import re
from dateutil import parser
from io import BytesIO

# --------------------
# Helper functions
# --------------------

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
        return t.strip().lower()

def normalize_times_list(tokens):
    return sorted(list({normalize_time(t) for t in tokens}))

def overlap(list1, list2):
    return any(i in list2 for i in list1)

def compute_score(child, vol):
    score = 0
    if overlap(child["_days"], vol["_days"]):
        score += 3
    if overlap(child["_times"], vol["_times"]):
        score += 3
    return score

# --------------------
# Streamlit App
# --------------------

st.title("📚 Strive Higher — Volunteer Matching Agent")

participants_file = st.file_uploader("Upload Participants Excel File", type="xlsx")
volunteers_file = st.file_uploader("Upload Volunteers Excel File", type="xlsx")

if participants_file and volunteers_file:

    # Load Excel files
    p = pd.read_excel(participants_file)
    v = pd.read_excel(volunteers_file)

    # --------------------
    # Auto-detect columns
    # --------------------
    P_DAYS = next((c for c in p.columns if "day" in c.lower()), None)
    P_TIMES = next((c for c in p.columns if "time" in c.lower()), None)

    V_DAYS = next((c for c in v.columns if "day" in c.lower()), None)
    V_TIMES = next((c for c in v.columns if "time" in c.lower()), None)

    # Validate columns
    if not P_DAYS or not P_TIMES:
        st.error("❌ Participant file is missing required Day or Time columns.")
        st.write("Columns found:", list(p.columns))
        st.stop()

    if not V_DAYS or not V_TIMES:
        st.error("❌ Volunteer file is missing required Day or Time columns.")
        st.write("Columns found:", list(v.columns))
        st.stop()

    # --------------------
    # Process participant fields
    # --------------------
    p["_days"] = p[P_DAYS].apply(split_list)
    p["_times"] = p[P_TIMES].apply(lambda x: normalize_times_list(split_list(x)))
    p["_langs"] = [[] for _ in range(len(p))]  # no language info
    p["Child_ID"] = p.index + 1

    # --------------------
    # Process volunteer fields
    # --------------------
    v["_days"] = v[V_DAYS].apply(split_list)
    v["_times"] = v[V_TIMES].apply(lambda x: normalize_times_list(split_list(x)))
    v["_langs"] = [[] for _ in range(len(v))]
    v["Volunteer_ID"] = v.index + 1

    # --------------------
    # Matching
    # --------------------
    assigned_volunteers = set()
    matches = []

    for _, child in p.iterrows():
        best_score = -1
        best_vol = None
        for _, vol in v.iterrows():
            if vol["Volunteer_ID"] in assigned_volunteers:
                continue  # skip already assigned volunteers
            score = compute_score(child, vol)
            if score > best_score:
                best_score = score
                best_vol = vol["Volunteer_ID"]

        if best_vol is not None:
            assigned_volunteers.add(best_vol)

        matches.append({
            "Child ID": child["Child_ID"],
            "Best Volunteer ID": best_vol,
            "Match Score": best_score
        })

    result = pd.DataFrame(matches)

    st.success("🎉 Matching complete!")
    st.dataframe(result)

    # --------------------
    # Download button
    # --------------------
    output = BytesIO()
    result.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)

    st.download_button(
        "Download Matches",
        data=output,
        file_name="matches.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
