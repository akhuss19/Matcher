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
    """Weighted matching: day + time."""
    score = 0
    if overlap(child["_days"], vol["_days"]):
        score += 3
    if overlap(child["_times"], vol["_times"]):
        score += 3
    return score

# ============================
# MAIN MATCHING FUNCTION
# ============================

def run_matching(participants_path, volunteers_path, output_path="matches.xlsx"):

    # Load data
    p = pd.read_excel(participants_path)
    v = pd.read_excel(volunteers_path)

    # Auto-detect columns by keyword
    P_DAYS = next((c for c in p.columns if "day" in c.lower()), None)
    P_TIMES = next((c for c in p.columns if "time" in c.lower()), None)
    V_DAYS = next((c for c in v.columns if "day" in c.lower()), None)
    V_TIMES = next((c for c in v.columns if "time" in c.lower()), None)

    if not P_DAYS or not P_TIMES:
        raise KeyError(f"Participant file missing Day or Time columns. Found: {list(p.columns)}")
    if not V_DAYS or not V_TIMES:
        raise KeyError(f"Volunteer file missing Day or Time columns. Found: {list(v.columns)}")

    # Clean participant data
    p["_days"] = p[P_DAYS].apply(split_list)
    p["_times"] = p[P_TIMES].apply(lambda x: normalize_times_list(split_list(x)))
    p["_langs"] = [[] for _ in range(len(p))]  # always empty
    p["Child_ID"] = p.index + 1

    # Clean volunteer data
    v["_days"] = v[V_DAYS].apply(split_list)
    v["_times"] = v[V_TIMES].apply(lambda x: normalize_times_list(split_list(x)))
    v["_langs"] = [[] for _ in range(len(v))]  # always empty
    v["Volunteer_ID"] = v.index + 1

    # Perform matching
    matches = []
    for _, child in p.iterrows():
        best_score = -1
        best_vol = None
        for _, vol in v.iterrows():
            score = compute_score(child, vol)
            if score > best_score:
                best_score = score
                best_vol = vol["Volunteer_ID"]
        matches.append({
            "Child ID": child["Child_ID"],
            "Best Volunteer ID": best_vol,
            "Match Score": best_score
        })

    result = pd.DataFrame(matches)
    result.to_excel(output_path, index=False)
    print(f"Matches saved to {output_path}")
    return result

if __name__ == "__main__":
    run_matching("participants.xlsx", "volunteers.xlsx")
