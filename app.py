import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import math

st.set_page_config(page_title="Knockout Bracket", layout="centered")
st.title("🏸 Knockout Tournament Bracket")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is None:
    st.stop()

# Safe Excel read
df = pd.read_excel(uploaded_file, engine="openpyxl", usecols=["Team"], nrows=100)
teams = df["Team"].dropna().tolist()

if len(teams) < 2:
    st.error("At least 2 teams required")
    st.stop()

# Ensure power of 2
random.shuffle(teams)
next_pow = 2 ** math.ceil(math.log2(len(teams)))
teams += ["BYE"] * (next_pow - len(teams))


def draw_bracket(teams):
    rounds = []
    current = teams.copy()

    while len(current) > 1:
        round_matches = []
        for i in range(0, len(current), 2):
            round_matches.append((current[i], current[i+1]))
        rounds.append(round_matches)
        current = [f"Winner {i+1}" for i in range(len(round_matches))]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis("off")

    x_gap = 2
    y_gap = 1

    positions = {}
    for r, matches in enumerate(rounds):
        x = r * x_gap
        for i, (t1, t2) in enumerate(matches):
            y1 = i * 2 * y_gap
            y2 = y1 - y_gap
            positions[(r, i, 0)] = (x, y1)
            positions[(r, i, 1)] = (x, y2)

            ax.text(x, y1, t1, ha="right", va="center")
            ax.text(x, y2, t2, ha="right", va="center")

            ax.plot([x, x + 0.5], [y1, y1], lw=1)
            ax.plot([x, x + 0.5], [y2, y2], lw=1)
            ax.plot([x + 0.5, x + 0.5], [y2, y1], lw=1)

            ax.plot([x + 0.5, x + x_gap], [(y1+y2)/2]*2, lw=1)

    ax.text(x + x_gap, 0, "🏆 Champion", fontsize=12, ha="left")
    return fig


if st.button("Generate Bracket"):
    fig = draw_bracket(teams)
    st.pyplot(fig)
    st.success("Knockout bracket generated!")
