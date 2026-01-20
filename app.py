import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import math
from io import BytesIO

# ---------------- PAGE SETUP ----------------
st.set_page_config(page_title="Tournament Draw Generator", layout="centered")
st.title("Tournament Draw Generator")

# ---------------- INPUT SECTION ----------------
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

draw_type = st.radio(
    "Select Tournament Type",
    ["🌱 Seeded Draws", "🔁 Round Robin", "🏆 Knockout Brackets"]
)

if uploaded_file is None:
    st.info("Please upload an Excel file to continue")
    st.stop()

# ---------------- SAFE EXCEL READ ----------------
try:
    df = pd.read_excel(
        uploaded_file,
        engine="openpyxl",
        usecols=lambda c: c in ["Team", "Seed"],
        nrows=200
    )
except Exception as e:
    st.error("❌ Unable to read Excel file")
    st.exception(e)
    st.stop()

if "Team" not in df.columns:
    st.error("Excel must contain a 'Team' column")
    st.stop()

teams = df["Team"].dropna().tolist()

if len(teams) < 2:
    st.error("At least 2 teams are required")
    st.stop()

# ---------------- HELPERS ----------------
def to_excel(df_dict):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet, data in df_dict.items():
            data.to_excel(writer, sheet_name=sheet, index=False)
    output.seek(0)
    return output

# ---------------- DRAW LOGIC ----------------
def seeded_draw(df):
    if "Seed" not in df.columns:
        st.error("Seed column required for Seeded Draws")
        return []

    df = df.dropna(subset=["Seed"]).sort_values("Seed")
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
            t1 = teams[i]
            t2 = teams[n - 1 - i]
            if t1 != "BYE" and t2 != "BYE":
                matches.append((t1, t2))
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

# ---------------- GENERATE OUTPUT ----------------
if st.button("Generate Draw"):
    if draw_type == "🌱 Seeded Draws":
        matches = seeded_draw(df)
        result_df = pd.DataFrame(matches, columns=["Team 1", "Team 2"])
        st.subheader("Seeded Matches")
        st.dataframe(result_df)

        excel_file = to_excel({"Seeded Draws": result_df})
        st.download_button(
            "📥 Download Seeded Draw (Excel)",
            excel_file,
            file_name="seeded_draws.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    elif draw_type == "🔁 Round Robin":
        rounds = round_robin_draw(teams)
        excel_sheets = {}

        for i, rnd in enumerate(rounds, 1):
            df_round = pd.DataFrame(rnd, columns=["Team 1", "Team 2"])
            st.subheader(f"Round {i}")
            st.dataframe(df_round)
            excel_sheets[f"Round {i}"] = df_round

        excel_file = to_excel(excel_sheets)
        st.download_button(
            "📥 Download Round Robin Schedule (Excel)",
            excel_file,
            file_name="round_robin_schedule.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    elif draw_type == "🏆 Knockout Brackets":
        fig = knockout_bracket(teams)
        st.pyplot(fig)

        img_buffer = BytesIO()
        fig.savefig(img_buffer, format="png", bbox_inches="tight")
        img_buffer.seek(0)

        st.download_button(
            "📥 Download Knockout Bracket (PNG)",
            img_buffer,
            file_name="knockout_bracket.png",
            mime="image/png"
        )

    st.success("✅ Draw generated successfully!")
