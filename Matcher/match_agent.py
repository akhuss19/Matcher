import pandas as pd
import re
from dateutil import parser

# ============================
# Helper Functions
# ============================

def split_list(cell):
    """Turn comma/semicolon separated values into a clean lowercase list."""
    if pd.isna(cell):
        return []
    items = re.split(r"[;,/]+", str(cell))
    return [i.strip().lower() for i in items if i.strip()]

def normalize_time(t):
    """Convert times like '4pm' or '4:00 PM' into '16:00' format."""
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
    """Weighted matching: day + time + language."""
    score = 0

    if overlap(child["_days"], vol["_days"]):
        score += 3
    
    if overlap(child["_times"], vol["_times"]):
        score += 3
    
    if overlap(child["_langs"], vol["_langs"]):
        score += 4

    return score

# ============================
# MAIN MATCHING FUNCTION
# ============================

def run_matching(participants_path, volunteers_path, output_path="matches.xlsx"):
    # Load data
    p = pd.read_excel(participants_path)
    v = pd.read_excel(volunteers_path)

    # Column names based on your real files
    P_NAME = "Student's Full Name"
    P_DAYS = "Day Availability  (one day will be assigned)-  please select at least two days"
    P_TIMES = "Please check off the times that you & your child would be available  (a specific time will be determined)-  please select at least two times"

    # Participants don’t have a clear language field → inferred from notes if needed
    P_LANG = None  

    V_NAME = "Volunteer Emailed"
    V_DAYS = "Day(s) Available-  Please select at least two days"
    V_TIMES = "Time Availability (Sessions are 30min- 1 hour long)- Please select at least two times"
    V_LANG = "Do you speak another language? If so, please include it below."

    # Clean participant fields
    p["_days"] = p[P_DAYS].apply(split_list)
    p["_times"] = p[P_TIMES].apply(lambda x: normalize_times_list(split_list(x)))

    if P_LANG and P_LANG in p.columns:
        p["_langs"] = p[P_LANG].apply(split_list)
    else:
        p["_langs"] = [[] for _ in range(len(p))]

    # Clean volunteer fields
    v["_days"] = v[V_DAYS].apply(split_list)
    v["_times"] = v[V_TIMES].apply(lambda x: normalize_times_list(split_list(x)))

    if V_LANG in v.columns:
        v["_langs"] = v[V_LANG].apply(split_list)
    else:
        v["_langs"] = [[] for _ in range(len(v))]

    matches = []

    # Choose best volunteer for each child
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
    result.to_excel(output_path, index=False)
    print(f"Matches saved to {output_path}")

    return result

if __name__ == "__main__":
    run_matching(
        "Copy of Fall 2025- Spring 2026 Virtual Reading Buddy- Participant Application (Responses).xlsx",
        "Copy of 2025-2026 Virtual Reading Buddy- Volunteer form (Responses).xlsx"
    )