import pandas as pd
import streamlit as st
from pathlib import Path

# ---------------------------------------------------------
# Config
# ---------------------------------------------------------
CSV_PATH = Path(__file__).with_name("Novice.csv")

# ---------------------------------------------------------
# Load and clean data
# ---------------------------------------------------------
@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df = df[df["Name"].notna() & df["Dots"].notna()]
    df["Dots"] = pd.to_numeric(df["Dots"], errors="coerce")
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce", dayfirst=True)
    return df

# ---------------------------------------------------------
# Determine Division by Age + Sex
# ---------------------------------------------------------
def assign_division(row):
    if pd.isna(row["Age"]):
        return None
    age = row["Age"]
    if age < 24:
        div = "Junior"
    elif age < 40:
        div = "Open"
    else:
        div = "Masters"
    gender = "Men" if str(row["Sex"]).strip().upper().startswith("M") else "Women"
    return f"{div} {gender}"

# ---------------------------------------------------------
# Apply Novice League rules
# ---------------------------------------------------------
def process_novice(df):
    df = df.copy()
    df["Division"] = df.apply(assign_division, axis=1)

    # Sort oldest first so most recent are dropped if >3
    df = df.sort_values("Date")

    # Keep up to first 3 appearances per lifter
    df["Appearances"] = df.groupby("Name").cumcount() + 1
    df = df[df["Appearances"] <= 3]

    # Sum DOTS for each athlete
    agg = (
        df.groupby(["Name", "Sex", "Division"], as_index=False)["Dots"]
        .sum()
        .sort_values("Dots", ascending=False)
    )

    # Rank within Division
    agg["Rank"] = agg.groupby("Division")["Dots"].rank(ascending=False, method="min")
    return agg

# ---------------------------------------------------------
# Display leaderboard
# ---------------------------------------------------------
def render_leaderboard(df):
    # Center and size the content nicely
    st.markdown(
        """
        <style>
        section.main > div {max-width: 800px !important; margin: auto;}
        .stDataFrame {width: fit-content !important; margin: auto;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("## 🏆 WRPF UK Novice League Leaderboard")

    st.markdown(
        """
        **WRPF UK Novice League Results**  
        The WRPF UK Novice League highlights developing lifters and provides a platform to gain experience in a supportive, competitive setting.  
        Eligibility is limited to those who have competed in **two or fewer events** (this event can be your third).  

        League placings are calculated by adding each lifter’s **DOTS score** from every Novice League event they compete in, capped at a maximum of three events.  
        At the end of the WRPF UK competitive calendar, the top three lifters in each division will receive prizes.  

        Final prize details are being confirmed with our sponsors and will be announced once finalised.  

        ---
        **Novice League Event Locations:**  
        • Nottingham Strong, Nottingham  
        • Raw Strength Gym, Warrington  
        • 349 Barbell, Salisbury  
        • Iron Warehouse Gym, Great Yarmouth  

        Current Results
        19/10/25 - Raw Strength Novice, Warrington
        
        Competitive Year:  
        The Novice League season runs from October 1st to September 30th each year.  
        ---
        """,
        unsafe_allow_html=True,
    )

    divisions = [
        "Open Men",
        "Open Women",
        "Junior Men",
        "Junior Women",
        "Masters Men",
        "Masters Women",
    ]
    tabs = st.tabs(divisions)

    for tab, div in zip(tabs, divisions):
        with tab:
            sub = df[df["Division"] == div]
            if sub.empty:
                st.info(f"No data for {div}")
            else:
                st.dataframe(
                    sub[["Rank", "Name", "Dots"]],
                    hide_index=True,
                    use_container_width=False,
                )
                st.download_button(
                    f"📥 Download {div} CSV",
                    sub.to_csv(index=False),
                    file_name=f"{div.replace(' ', '_')}.csv",
                    key=div,
                )

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main():
    st.set_page_config("WRPF UK Novice League", layout="wide")
    df = load_data(CSV_PATH)
    processed = process_novice(df)
    render_leaderboard(processed)

if __name__ == "__main__":
    main()






