import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import math

st.set_page_config(page_title="Tournament Draw Generator", layout="centered")
st.title("Tournament Draw Generator")

# ---------------- FIRST SCREEN ----------------
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

draw_type = st.radio(
    "Select Tournament Type",
    ["Seeded Draws", "Round Robin", "Knockout Brackets"]
)

if uploaded_file is None:
    st.info("Upload an Excel file to continue")
    st.stop()

# ---------------- READ EXCEL SAFELY ----------------
try:
    df = pd.read_excel(
        uploaded_file,
        engine="openpyxl",
        usecols=lambda c: c in ["Team", "Seed"],
        nrows=100
    )
except Exception as e:
    st.error("Unable to read Excel file")
    st.exception(e)
    st.stop()

if "Team" not in df.columns:
    st.error("Excel must contain 'Team' column")
    st.stop()

teams = df["Team"].dropna().tolist()

if len(teams) < 2:
    st.error("At least 2 teams required")
    st.stop()

# ---------------- DRAW LOGIC ----------------
def seeded_draw(df):
    if "Seed" not in df.columns:
        st.error("Seed column required for Seeded Draws")
        return []

    df = df.sort_values("Seed")
    teams = df["Team"].tolist()
    matches = []

    if len(teams) % 2 != 0:
        matches.append((teams.pop(), "BYE"))

    for i in range(len(teams) // 2):
        matches.append((teams[i], teams[-(i + 1)]))

    return matches


def round_robin_draw(team_list):
    teams = team_list.copy()
    if len(teams) % 2 != 0:
        teams.append("BYE")

    n = len(teams)
    rounds = []

    for _ in range(n - 1):
        matches = []
        for i in range(n // 2):
            if teams[i] != "BYE" and teams[n - 1 - i] != "BYE":
                matches.append((teams[i], teams[n - 1 - i]))
        rounds.append(matches)
        teams = [teams[0]] + teams[-1:] + teams[1:-1]

    return rounds


def knockout_bracket(team_list):
    teams = team_list.copy()
    random.shuffle(teams)

    next_pow = 2 ** math.ceil(math.log2(len(teams)))
    teams += ["BYE"] * (next_pow - len(teams))

    rounds = []
    current = teams

    while len(current) > 1:
        matches = [(current[i], current[i + 1]) for i in range(0, len(current), 2)]
        rounds.append(matches)
        current = [f"Winner {i + 1}" for i in range(len(matches))]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis("off")

    x_gap, y_gap = 2, 1

    for r, matches in enumerate(rounds):
        x = r * x_gap
        for i, (t1, t2) in enumerate(matches):
            y1 = i * 2 * y_gap
            y2 = y1 - y_gap

            ax.text(x, y1, t1, ha="right", va="center")
            ax.text(x, y2, t2, ha="right", va="center")

            ax.plot([x, x + 0.5], [y1, y1])
            ax.plot([x, x + 0.5], [y2, y2])
            ax.plot([x + 0.5, x + 0.5], [y2, y1])
            ax.plot([x + 0.5, x + x_gap], [(y1 + y2) / 2] * 2)

    ax.text(x + x_gap, 0, "🏆 Champion", fontsize=12)
    return fig

# ---------------- GENERATE ----------------
if st.button("Generate Draw"):
    if draw_type == "🌱 Seeded Draws":
        matches = seeded_draw(df)
        st.subheader("Seeded Matches")
        st.dataframe(pd.DataFrame(matches, columns=["Team 1", "Team 2"]))

    elif draw_type == "🔁 Round Robin":
        rounds = round_robin_draw(teams)
        for i, rnd in enumerate(rounds, 1):
            st.subheader(f"Round {i}")
            st.dataframe(pd.DataFrame(rnd, columns=["Team 1", "Team 2"]))

    elif draw_type == "🏆 Knockout Brackets":
        fig = knockout_bracket(teams)
        st.pyplot(fig)

    st.success("Draw generated successfully!")
