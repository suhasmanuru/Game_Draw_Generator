import streamlit as st
import pandas as pd
import random
import math

st.set_page_config(page_title="Badminton Match Draws", layout="centered")
st.title("🏸 Badminton Tournament Match Draw Generator")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

# STOP app execution until file is uploaded
if uploaded_file is None:
    st.info("Please upload an Excel file to continue")
    st.stop()

# SAFE Excel read
try:
    df = pd.read_excel(uploaded_file, engine="openpyxl")
except Exception as e:
    st.error("❌ Unable to read Excel file")
    st.exception(e)
    st.stop()

# VALIDATE INPUT
if "Team" not in df.columns:
    st.error("Excel must contain a 'Team' column")
    st.stop()

teams = df["Team"].dropna().tolist()

draw_type = st.selectbox(
    "Select Draw Type",
    ["Random Draw", "Seeded Draw", "Round Robin", "Knockout Bracket"]
)

# ---------------- FUNCTIONS ----------------
def random_draw(teams):
    random.shuffle(teams)
    matches = []

    if len(teams) % 2 != 0:
        matches.append((teams.pop(), "BYE"))

    for i in range(0, len(teams), 2):
        matches.append((teams[i], teams[i + 1]))

    return matches

def seeded_draw(df):
    if "Seed" not in df.columns:
        st.error("Seed column missing for seeded draw")
        return []

    df = df.sort_values("Seed")
    teams = df["Team"].tolist()
    matches = []

    if len(teams) % 2 != 0:
        matches.append((teams.pop(), "BYE"))

    for i in range(len(teams) // 2):
        matches.append((teams[i], teams[-(i + 1)]))

    return matches

def round_robin(teams):
    if len(teams) % 2 != 0:
        teams.append("BYE")

    n = len(teams)
    rounds = []

    for r in range(n - 1):
        round_matches = []
        for i in range(n // 2):
            if teams[i] != "BYE" and teams[n - 1 - i] != "BYE":
                round_matches.append((teams[i], teams[n - 1 - i]))
        rounds.append(round_matches)
        teams = [teams[0]] + teams[-1:] + teams[1:-1]

    return rounds

def knockout(teams):
    random.shuffle(teams)
    matches = []

    power = 2 ** math.ceil(math.log2(len(teams)))
    byes = power - len(teams)
    teams.extend(["BYE"] * byes)

    for i in range(0, len(teams), 2):
        matches.append((teams[i], teams[i + 1]))

    return matches

# ---------------- GENERATE ----------------
if st.button("Generate Matches"):
    if draw_type == "Random Draw":
        matches = random_draw(teams.copy())
        st.dataframe(pd.DataFrame(matches, columns=["Team 1", "Team 2"]))

    elif draw_type == "Seeded Draw":
        matches = seeded_draw(df)
        st.dataframe(pd.DataFrame(matches, columns=["Team 1", "Team 2"]))

    elif draw_type == "Round Robin":
        rounds = round_robin(teams.copy())
        for i, rnd in enumerate(rounds, 1):
            st.subheader(f"Round {i}")
            st.dataframe(pd.DataFrame(rnd, columns=["Team 1", "Team 2"]))

    elif draw_type == "Knockout Bracket":
        matches = knockout(teams.copy())
        st.dataframe(pd.DataFrame(matches, columns=["Team 1", "Team 2"]))

    st.success("✅ Matches generated successfully!")
