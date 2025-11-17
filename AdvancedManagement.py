import pandas as pd

# Load data
volunteers = pd.read_csv("Volunteers.csv")
students = pd.read_csv("Students.csv")

matches = []

for _, student in students.iterrows():
    # Find volunteer who shares language and availability
    match = volunteers[
        (volunteers["Language"] == student["Language"]) &
        (volunteers["Availability"].str.contains(student["Availability"]))
    ]
    if not match.empty:
        volunteer = match.iloc[0]
        matches.append({
            "Student": student["Name"],
            "Volunteer": volunteer["Name"],
            "VolunteerEmail": volunteer["Email"],
            "StudentEmail": student["Email"]
        })
        # Remove matched volunteer so they aren't reused
        volunteers = volunteers.drop(volunteer.name)

matches_df = pd.DataFrame(matches)
matches_df.to_csv("Matches.csv", index=False)
print("✅ Matches created and saved!")