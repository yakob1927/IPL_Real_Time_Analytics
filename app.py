
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="IPL Analytics | Pro Dashboard",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# PROFESSIONAL CSS DESIGN
# ==========================================

st.markdown("""
<style>
    .stApp {
        background-color: #0b1120;
        color: #f1f5f9;
    }

    [data-testid="stSidebar"] {
        background-color: #111827;
    }

    [data-testid="stMetric"] {
        background-color: #172238;
        border: 1px solid #263750;
        padding: 20px;
        border-radius: 12px;
    }

    [data-testid="stMetricLabel"] {
        color: #94a3b8;
    }

    [data-testid="stMetricValue"] {
        color: #38bdf8;
    }

    h1, h2, h3 {
        color: #f8fafc;
    }

    .main-header {
        font-size: 34px;
        font-weight: 800;
        color: #38bdf8;
        margin-bottom: 0;
    }

    .sub-header {
        color: #94a3b8;
        font-size: 14px;
        margin-bottom: 25px;
    }

    .section-header {
        color: #38bdf8;
        font-size: 21px;
        font-weight: 700;
        margin-top: 15px;
    }

    div[data-testid="stTabs"] button {
        color: #cbd5e1;
    }

    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #38bdf8;
    }

    .stButton button {
        background-color: #0284c7;
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 600;
    }

    footer {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# HEADER
# ==========================================

st.markdown(
    '<div class="main-header">🏏 IPL ANALYTICS PRO</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-header">'
    'Professional Cricket Analytics | Historical IPL Data | Player Insights'
    '</div>',
    unsafe_allow_html=True
)

# ==========================================
# DATA LOADING
# ==========================================

DATA_FILE = Path("data/ipl_deliveries.csv")


@st.cache_data
def load_data():

    df = pd.read_csv(DATA_FILE)

    df["season"] = df["season"].astype("string").str.strip()

    numeric_columns = [
        "total_runs",
        "batter_runs",
        "wides",
        "noballs",
        "is_wicket",
        "innings",
        "over",
        "ball"
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col], errors="coerce"
            ).fillna(0)

    return df


if not DATA_FILE.exists():
    st.error("IPL dataset not found. Run python prepare_data.py first.")
    st.stop()

try:
    df = load_data()
except Exception as error:
    st.error(f"Data loading error: {error}")
    st.stop()

if df.empty:
    st.error("The dataset is empty.")
    st.stop()

# ==========================================
# SIDEBAR FILTERS
# ==========================================

st.sidebar.markdown("## ⚙️ Dashboard Controls")
st.sidebar.caption("Customize your IPL analysis")

seasons = sorted(
    df["season"].dropna().unique().tolist(),
    key=lambda x: int("".join(
        c for c in str(x) if c.isdigit()
    )[:4] or 0)
)

selected_seasons = st.sidebar.multiselect(
    "Select Season",
    seasons,
    default=seasons
)

teams = sorted(
    df["batting_team"].dropna().unique().tolist()
) if "batting_team" in df.columns else []

selected_teams = st.sidebar.multiselect(
    "Select Teams",
    teams,
    default=teams
)

if not selected_seasons:
    st.warning("Select at least one season.")
    st.stop()

filtered_df = df[
    df["season"].isin(selected_seasons)
].copy()

if selected_teams and "batting_team" in filtered_df.columns:
    filtered_df = filtered_df[
        filtered_df["batting_team"].isin(selected_teams)
    ]

if filtered_df.empty:
    st.warning("No data available for these filters.")
    st.stop()

st.sidebar.divider()
st.sidebar.caption("Data source: Cricsheet IPL ball-by-ball dataset")
st.sidebar.caption("Built with Python • Streamlit • Plotly")

# ==========================================
# MATCH LEVEL DATA
# ==========================================

if "match_id" in filtered_df.columns:

    match_df = (
        filtered_df.sort_values(
            ["match_id", "innings", "over", "ball"]
        )
        .drop_duplicates("match_id")
        .copy()
    )

else:
    match_df = filtered_df.copy()

total_matches = (
    match_df["match_id"].nunique()
    if "match_id" in match_df.columns else 0
)

total_runs = int(filtered_df["total_runs"].sum())

total_wickets = int(filtered_df["is_wicket"].sum())

total_teams = (
    filtered_df["batting_team"].nunique()
    if "batting_team" in filtered_df.columns else 0
)

# ==========================================
# KPI CARDS
# ==========================================

st.markdown("### 📊 Tournament Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Matches", f"{total_matches:,}")
c2.metric("Total Runs", f"{total_runs:,}")
c3.metric("Total Wickets", f"{total_wickets:,}")
c4.metric("Active Teams", f"{total_teams:,}")

st.divider()

# ==========================================
# MAIN TABS
# ==========================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🏏 Players",
    "🏆 Teams",
    "📅 Match Explorer",
    "🔮 Predictions"
])

# Common chart style
CHART_TEMPLATE = "plotly_dark"

# ==========================================
# TAB 1: OVERVIEW
# ==========================================

with tab1:

    st.markdown("### 📈 IPL Performance Overview")

    left, right = st.columns(2)

    with left:

        st.markdown("#### Runs by Season")

        season_runs = (
            filtered_df.groupby("season")["total_runs"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            season_runs,
            x="season",
            y="total_runs",
            color="total_runs",
            color_continuous_scale="Blues",
            text_auto=True,
            template=CHART_TEMPLATE
        )

        fig.update_layout(
            xaxis_title="Season",
            yaxis_title="Total Runs",
            coloraxis_showscale=False
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:

        st.markdown("#### Runs Distribution")

        fig = px.histogram(
            filtered_df,
            x="total_runs",
            nbins=15,
            template=CHART_TEMPLATE,
            color_discrete_sequence=["#38bdf8"]
        )

        fig.update_layout(
            xaxis_title="Runs per Delivery",
            yaxis_title="Delivery Count"
        )

        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    left, right = st.columns(2)

    with left:

        st.markdown("#### Top 10 Winning Teams")

        if "winner" in match_df.columns:

            wins = (
                match_df["winner"]
                .dropna()
                .value_counts()
                .head(10)
                .reset_index()
            )

            wins.columns = ["Team", "Wins"]

            fig = px.bar(
                wins,
                x="Wins",
                y="Team",
                orientation="h",
                text="Wins",
                template=CHART_TEMPLATE,
                color="Wins",
                color_continuous_scale="Blues"
            )

            fig.update_layout(
                yaxis={"categoryorder": "total ascending"},
                coloraxis_showscale=False
            )

            st.plotly_chart(fig, use_container_width=True)

    with right:

        st.markdown("#### Wicket Distribution")

        if "is_wicket" in filtered_df.columns:

            wicket_count = filtered_df["is_wicket"].sum()
            safe_deliveries = len(filtered_df) - wicket_count

            fig = go.Figure(data=[go.Pie(
                labels=["Wickets", "No Wicket"],
                values=[wicket_count, safe_deliveries],
                hole=0.65
            )])

            fig.update_layout(
                template=CHART_TEMPLATE
            )

            st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 2: PLAYER ANALYTICS
# ==========================================

with tab2:

    st.markdown("### 🏏 Player Performance Center")

    if "batter" in filtered_df.columns:

        player_runs = (
            filtered_df.groupby("batter")["batter_runs"]
            .sum()
            .reset_index()
        )

        player_runs.columns = ["Player", "Runs"]

        player_runs = player_runs.sort_values(
            "Runs", ascending=False
        )

        col1, col2 = st.columns([1.3, 1])

        with col1:

            st.markdown("#### Top Run Scorers")

            fig = px.bar(
                player_runs.head(10),
                x="Runs",
                y="Player",
                orientation="h",
                text="Runs",
                template=CHART_TEMPLATE,
                color="Runs",
                color_continuous_scale="Blues"
            )

            fig.update_layout(
                yaxis={"categoryorder": "total ascending"},
                coloraxis_showscale=False
            )

            st.plotly_chart(fig, use_container_width=True)

        with col2:

            st.markdown("#### Player Statistics")

            player_stats = filtered_df.copy()

            if "wides" in player_stats.columns:
                player_stats["balls_faced"] = (
                    player_stats["wides"] == 0
                ).astype(int)
            else:
                player_stats["balls_faced"] = 1

            stats = (
                player_stats.groupby("batter")
                .agg(
                    Runs=("batter_runs", "sum"),
                    Balls=("balls_faced", "sum")
                )
                .reset_index()
            )

            stats = stats[stats["Balls"] > 0]

            stats["Strike Rate"] = (
                stats["Runs"] / stats["Balls"] * 100
            ).round(2)

            stats = stats.sort_values(
                "Runs", ascending=False
            )

            st.dataframe(
                stats.head(15),
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        st.markdown("#### Individual Player Analysis")

        selected_player = st.selectbox(
            "Choose a Player",
            sorted(filtered_df["batter"].dropna().unique())
        )

        individual = filtered_df[
            filtered_df["batter"] == selected_player
        ]

        p1, p2 = st.columns(2)

        p1.metric(
            "Total Runs",
            int(individual["batter_runs"].sum())
        )

        p2.metric(
            "Total Deliveries",
            len(individual)
        )

# ==========================================
# TAB 3: TEAM ANALYSIS
# ==========================================

with tab3:

    st.markdown("### 🏆 Team Performance Center")

    if "batting_team" in filtered_df.columns:

        team_runs = (
            filtered_df.groupby("batting_team")["total_runs"]
            .sum()
            .reset_index()
        )

        team_runs.columns = ["Team", "Total Runs"]

        team_runs = team_runs.sort_values(
            "Total Runs", ascending=False
        )

        fig = px.bar(
            team_runs,
            x="Team",
            y="Total Runs",
            color="Total Runs",
            text_auto=True,
            template=CHART_TEMPLATE,
            color_continuous_scale="Blues"
        )

        fig.update_layout(
            coloraxis_showscale=False
        )

        st.plotly_chart(fig, use_container_width=True)

    if "toss_winner" in match_df.columns:

        st.markdown("#### Toss Wins by Team")

        toss_data = (
            match_df["toss_winner"]
            .dropna()
            .value_counts()
            .reset_index()
        )

        toss_data.columns = ["Team", "Toss Wins"]

        fig = px.pie(
            toss_data,
            names="Team",
            values="Toss Wins",
            hole=0.5,
            template=CHART_TEMPLATE
        )

        st.plotly_chart(fig, use_container_width=True)

# ==========================================
# TAB 4: MATCH EXPLORER
# ==========================================

with tab4:

    st.markdown("### 📅 IPL Match Explorer")

    if "match_id" in filtered_df.columns:

        match_options = sorted(
            filtered_df["match_id"].dropna().unique().tolist()
        )

        selected_match = st.selectbox(
            "Select Match ID",
            match_options
        )

        selected_match_df = filtered_df[
            filtered_df["match_id"] == selected_match
        ]

        if "venue" in selected_match_df.columns:

            venue = selected_match_df["venue"].dropna()

            if not venue.empty:
                st.write(f"**Venue:** {venue.iloc[0]}")

        if "date" in selected_match_df.columns:

            match_date = selected_match_df["date"].dropna()

            if not match_date.empty:
                st.write(f"**Date:** {match_date.iloc[0]}")

        if "winner" in selected_match_df.columns:

            winner = selected_match_df["winner"].dropna()

            if not winner.empty:
                st.success(f"🏆 Winner: {winner.iloc[0]}")

        innings_summary = (
            selected_match_df.groupby("innings")
            .agg(
                Runs=("total_runs", "sum"),
                Wickets=("is_wicket", "sum")
            )
            .reset_index()
        )

        st.dataframe(
            innings_summary,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("#### Ball-by-Ball Data")

        st.dataframe(
            selected_match_df,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("Match ID is not available in this dataset.")

# ==========================================
# TAB 5: WIN PROBABILITY ESTIMATOR
# ==========================================

with tab5:

    st.markdown("### 🔮 Match Win Probability Estimator")

    st.info(
        "Educational estimate based on match situation. "
        "This is not a trained or validated machine-learning model."
    )

    col1, col2 = st.columns(2)

    with col1:

        target = st.number_input(
            "Target Score",
            min_value=1,
            max_value=500,
            value=180
        )

        current_score = st.number_input(
            "Current Score",
            min_value=0,
            max_value=500,
            value=100
        )

    with col2:

        wickets = st.slider(
            "Wickets Lost",
            0, 10, 3
        )

        overs = st.slider(
            "Overs Completed",
            0, 19, 10
        )

        balls = st.slider(
            "Balls in Current Over",
            0, 5, 0
        )

    if st.button("Calculate Win Probability"):

        balls_bowled = overs * 6 + balls
        balls_remaining = max(120 - balls_bowled, 0)
        runs_needed = max(target - current_score, 0)

        if current_score >= target:
            probability = 100.0

        elif balls_remaining == 0 or wickets == 10:
            probability = 0.0

        else:

            required_rate = (
                runs_needed * 6 / balls_remaining
            )

            current_rate = (
                current_score * 6 / balls_bowled
                if balls_bowled > 0 else 0
            )

            rate_difference = current_rate - required_rate

            score = (
                0.8 * rate_difference
                + 0.25 * (5 - required_rate)
                + 2 * ((10 - wickets) / 10)
            )

            probability = (
                100 / (1 + np.exp(-np.clip(score, -20, 20)))
            )

        st.metric(
            "Estimated Chasing Team Win Probability",
            f"{probability:.2f}%"
        )

        st.progress(
            int(np.clip(probability, 0, 100))
        )

        st.write(f"Runs needed: **{runs_needed}**")
        st.write(f"Balls remaining: **{balls_remaining}**")

# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown(
    """
    <div style="text-align:center; color:#94a3b8;">
        IPL ANALYTICS PRO | Built using Python, Pandas,
        Streamlit and Plotly
        <br>
        Historical cricket analytics portfolio project
    </div>
    """,
    unsafe_allow_html=True
)
