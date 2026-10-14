from pathlib import Path

import joblib
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------- THEME ----------------
BG = "#101512"
CARD = "#1A211D"
ACCENT = "#A6E65C"
ACCENT_2 = "#5CC8E6"
WARN = "#F2B84B"
BAD = "#F0645A"
TEXT = "#EDEDE5"
MUTED = "#929B93"
GRID = "#2A332D"

MODEL_PATH = Path("models/ipl_chase_model.joblib")
SUMMARY_PATH = Path("data/processed/match_summary.csv")

st.set_page_config(page_title="IPL Analytics & Predictor", page_icon="🏏", layout="wide")

st.markdown(
    f"""
    <style>
    #MainMenu, footer {{visibility: hidden;}}
    .block-container {{padding-top: 1.5rem; max-width: 1250px;}}
    .hero {{
        background: linear-gradient(120deg, #1F2B22 0%, #14301F 55%, #1A211D 100%);
        border: 1px solid {GRID}; border-radius: 18px;
        padding: 26px 32px; margin-bottom: 18px;
    }}
    .hero h1 {{margin: 0; font-size: 2.1rem; color: {TEXT};}}
    .hero h1 span {{color: {ACCENT};}}
    .hero p {{margin: 6px 0 0; color: {MUTED}; font-size: 1rem;}}
    div[data-testid="stMetric"] {{
        background: {CARD}; border: 1px solid {GRID}; border-left: 4px solid {ACCENT};
        border-radius: 14px; padding: 14px 18px;
    }}
    div[data-testid="stMetricLabel"] p {{color: {MUTED}; font-size: .85rem;}}
    div[data-testid="stMetricValue"] {{color: {TEXT};}}
    .stTabs [data-baseweb="tab-list"] {{gap: 6px;}}
    .stTabs [data-baseweb="tab"] {{
        background: {CARD}; border-radius: 10px 10px 0 0; padding: 10px 18px;
    }}
    .stTabs [aria-selected="true"] {{background: #24301F; color: {ACCENT};}}
    .stButton > button[kind="primary"] {{
        background: {ACCENT}; color: #0E140F; border: none; font-weight: 700;
        border-radius: 10px; padding: .6rem 1.2rem;
    }}
    .stButton > button[kind="primary"]:hover {{background: #BDF27E; color: #0E140F;}}
    .panel {{background: {CARD}; border: 1px solid {GRID}; border-radius: 14px; padding: 18px;}}
    .verdict {{font-size: 1.1rem; font-weight: 600;}}
    </style>
    """,
    unsafe_allow_html=True,
)


def style_chart(fig, height=360, legend=False):
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Arial, sans-serif", color=TEXT, size=12),
        margin=dict(l=10, r=20, t=45, b=10),
        title_font=dict(size=16, color=TEXT),
        showlegend=legend,
        hoverlabel=dict(bgcolor="#252D28", font_color=TEXT),
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=MUTED))
    fig.update_yaxes(gridcolor=GRID, zeroline=False, tickfont=dict(color=TEXT))
    return fig


# ---------------- DATA ----------------
@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_summary():
    return pd.read_csv(SUMMARY_PATH)


st.markdown(
    """
    <div class="hero">
      <h1>🏏 IPL <span>Analytics</span> & Match Predictor</h1>
      <p>Explore historical matches, compare teams, and estimate live chase outcomes.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if not MODEL_PATH.exists() or not SUMMARY_PATH.exists():
    st.error("Required files are missing. Check the model and match summary paths.")
    st.stop()

model = load_model()
df = load_summary()

df["season_label"] = df["season"].fillna("Unknown").astype(str)
df["venue_label"] = df["venue"].fillna("Unknown").astype(str)

teams = sorted(set(df["team1"].dropna().astype(str)) | set(df["team2"].dropna().astype(str)))
seasons = sorted(df["season_label"].unique())
venues = sorted(df["venue_label"].unique())

# ---------------- SIDEBAR ----------------
st.sidebar.title("🔎 Match Filters")


def reset_filters():
    st.session_state["f_seasons"] = seasons
    st.session_state["f_teams"] = teams
    st.session_state["f_venues"] = venues


for key, default in (("f_seasons", seasons), ("f_teams", teams), ("f_venues", venues)):
    st.session_state.setdefault(key, default)

with st.sidebar.expander("📅 Seasons", expanded=True):
    selected_seasons = st.multiselect("Seasons", seasons, key="f_seasons", label_visibility="collapsed")
with st.sidebar.expander("🏆 Teams"):
    selected_teams = st.multiselect("Teams", teams, key="f_teams", label_visibility="collapsed")
with st.sidebar.expander("🏟️ Venues"):
    selected_venues = st.multiselect("Venues", venues, key="f_venues", label_visibility="collapsed")

st.sidebar.button("↺ Reset filters", on_click=reset_filters, use_container_width=True)

filtered = df[
    df["season_label"].isin(selected_seasons)
    & df["venue_label"].isin(selected_venues)
    & df["team1"].isin(selected_teams)
    & df["team2"].isin(selected_teams)
].copy()

st.sidebar.caption(f"{len(filtered):,} of {len(df):,} matches selected")

# ---------------- TABS ----------------
tab_over, tab_team, tab_venue, tab_toss, tab_pred = st.tabs(
    ["📊 Overview", "🏆 Teams", "🏟️ Venues", "🪙 Toss", "🎯 Chase Predictor"]
)

has_data = not filtered.empty

# ---------- OVERVIEW ----------
with tab_over:
    if not has_data:
        st.warning("No matches match these filters. Select more seasons, teams, or venues.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Matches", f"{len(filtered):,}")
        c2.metric("With winners", f"{filtered['winner'].notna().sum():,}")
        c3.metric("Venues", f"{filtered['venue_label'].nunique():,}")
        c4.metric("Seasons", f"{filtered['season_label'].nunique():,}")

        season_counts = filtered.groupby("season_label").size().reset_index(name="matches")
        fig = px.area(season_counts, x="season_label", y="matches", markers=True,
                      title="Matches played across seasons")
        fig.update_traces(
            line=dict(color=ACCENT, width=3),
            marker=dict(size=8, color=ACCENT),
            fillcolor="rgba(166,230,92,0.15)",
            hovertemplate="%{x}<br>Matches: %{y}<extra></extra>",
        )
        fig.update_xaxes(title=None, type="category")
        fig.update_yaxes(title=None)
        st.plotly_chart(style_chart(fig, 360), use_container_width=True)

# ---------- TEAMS ----------
with tab_team:
    if not has_data:
        st.warning("No data for the current filters.")
    else:
        left, right = st.columns([3, 2])

        with left:
            metric_choice = st.radio("Rank teams by", ["Total wins", "Win %"], horizontal=True)
            wins = filtered.dropna(subset=["winner"]).groupby("winner").size()
            played = pd.concat([filtered["team1"], filtered["team2"]]).value_counts()
            tbl = pd.DataFrame({"wins": wins, "played": played}).dropna()
            tbl["win_pct"] = (tbl["wins"] / tbl["played"] * 100).round(1)

            col = "wins" if metric_choice == "Total wins" else "win_pct"
            top_n = st.slider("Teams to show", 3, max(3, min(15, len(tbl))), min(10, max(3, len(tbl))))
            top = tbl.sort_values(col, ascending=False).head(top_n).sort_values(col).reset_index(names="team")

            fig = px.bar(top, x=col, y="team", orientation="h", text=col,
                         title=f"Top {top_n} teams by {metric_choice.lower()}",
                         color=col, color_continuous_scale=["#2F4A2A", ACCENT])
            fig.update_traces(textposition="outside", cliponaxis=False,
                              hovertemplate="%{y}<br>%{x}<extra></extra>")
            fig.update_coloraxes(showscale=False)
            fig.update_xaxes(title=None)
            fig.update_yaxes(title=None)
            st.plotly_chart(style_chart(fig, 120 + 38 * top_n), use_container_width=True)

        with right:
            st.subheader("⚔️ Head to head")
            t1 = st.selectbox("Team A", selected_teams or teams, index=0)
            options_b = [t for t in (selected_teams or teams) if t != t1]
            t2 = st.selectbox("Team B", options_b, index=0 if options_b else None)

            if t2:
                h2h = filtered[
                    ((filtered["team1"] == t1) & (filtered["team2"] == t2))
                    | ((filtered["team1"] == t2) & (filtered["team2"] == t1))
                ]
                a = int((h2h["winner"] == t1).sum())
                b = int((h2h["winner"] == t2).sum())
                st.metric("Matches played", len(h2h))
                if a + b > 0:
                    fig = go.Figure(go.Pie(
                        labels=[t1, t2], values=[a, b], hole=0.62,
                        marker=dict(colors=[ACCENT, ACCENT_2], line=dict(color=BG, width=3)),
                        textinfo="value", hovertemplate="%{label}: %{value}<extra></extra>",
                    ))
                    fig.update_layout(legend=dict(orientation="h", y=-0.05))
                    st.plotly_chart(style_chart(fig, 300, legend=True), use_container_width=True)
                else:
                    st.info("No decided matches between these teams in the current filters.")

# ---------- VENUES ----------
with tab_venue:
    if not has_data:
        st.warning("No data for the current filters.")
    else:
        n = st.slider("Venues to show", 5, 20, 10)
        vc = (filtered.groupby("venue_label").size().sort_values(ascending=False)
              .head(n).sort_values().reset_index(name="matches"))
        fig = px.bar(vc, x="matches", y="venue_label", orientation="h", text="matches",
                     title=f"Top {n} venues by match count")
        fig.update_traces(marker_color=ACCENT_2, textposition="outside", cliponaxis=False,
                          hovertemplate="%{y}<br>Matches: %{x}<extra></extra>")
        fig.update_xaxes(title=None)
        fig.update_yaxes(title=None)
        st.plotly_chart(style_chart(fig, 120 + 34 * n), use_container_width=True)

# ---------- TOSS ----------
with tab_toss:
    toss_df = filtered.dropna(subset=["toss_winner", "winner"]).copy()
    if toss_df.empty:
        st.info("No toss data is available for these filters.")
    else:
        toss_df["toss_winner_won_match"] = toss_df["toss_winner"] == toss_df["winner"]
        toss_df["toss_decision"] = toss_df["toss_decision"].fillna("Unknown")

        c1, c2 = st.columns(2)
        c1.metric("Toss winner also won", f"{toss_df['toss_winner_won_match'].mean():.1%}")
        c2.metric("Matches analysed", f"{len(toss_df):,}")

        left, right = st.columns(2)
        with left:
            dc = toss_df["toss_decision"].value_counts().reset_index()
            dc.columns = ["decision", "matches"]
            fig = px.pie(dc, names="decision", values="matches", hole=0.6, title="Toss decisions",
                         color_discrete_sequence=[ACCENT, ACCENT_2, WARN])
            fig.update_traces(marker=dict(line=dict(color=BG, width=3)))
            st.plotly_chart(style_chart(fig, 340, legend=True), use_container_width=True)
        with right:
            rate = (toss_df.groupby("toss_decision")["toss_winner_won_match"].mean() * 100).round(1).reset_index()
            rate.columns = ["decision", "win_pct"]
            fig = px.bar(rate, x="decision", y="win_pct", text="win_pct",
                         title="Match win % of toss winner, by decision")
            fig.update_traces(marker_color=ACCENT, textposition="outside",
                              hovertemplate="%{x}: %{y}%<extra></extra>")
            fig.update_xaxes(title=None)
            fig.update_yaxes(title=None, range=[0, 100])
            st.plotly_chart(style_chart(fig, 340), use_container_width=True)

        st.caption("Historical association does not prove that winning the toss causes a win.")

# ---------- PREDICTOR ----------
def build_state(team, target, runs, wkts, balls):
    balls_rem = 120 - balls
    runs_rem = target - runs
    return {
        "chasing_team": team,
        "target": target,
        "runs_scored": runs,
        "wickets_lost": wkts,
        "legal_balls_bowled": balls,
        "balls_remaining": balls_rem,
        "runs_remaining": runs_rem,
        "current_run_rate": runs * 6 / balls if balls else 0,
        "required_run_rate": runs_rem * 6 / balls_rem,
    }


def overs_text(balls):
    return f"{balls // 6}.{balls % 6}"


with tab_pred:
    st.write("Set the match situation and estimate the chasing team's chance of winning.")

    presets = {
        "Custom": None,
        "Start of chase (180 target)": (180, 0, 0, 0),
        "Mid-innings, on track": (180, 90, 3, 60),
        "Death overs, tight": (180, 150, 5, 100),
        "Needs a miracle": (200, 100, 7, 96),
    }
    preset = st.selectbox("Quick scenario", list(presets))
    p = presets[preset] or (180, 90, 3, 60)

    form, result = st.columns([2, 3], gap="large")

    with form:
        default_team = "Mumbai Indians" if "Mumbai Indians" in teams else teams[0]
        team = st.selectbox("Chasing team", teams, index=teams.index(default_team))
        target = st.number_input("Target runs", 1, 500, p[0])
        runs_scored = st.number_input("Runs scored", 0, 500, p[1])
        wickets_lost = st.slider("Wickets lost", 0, 10, p[2])
        legal_balls = st.slider("Legal balls bowled", 0, 120, p[3], help="6 balls = 1 over")
        st.caption(f"Overs completed: **{overs_text(legal_balls)}**")
        go_btn = st.button("Predict win probability", type="primary", use_container_width=True)

    with result:
        if not go_btn:
            st.markdown(
                '<div class="panel">👈 Set the scenario and press <b>Predict</b> to see the '
                "win probability, gauge, and how wickets change the outlook.</div>",
                unsafe_allow_html=True,
            )
        elif runs_scored >= target:
            st.success("The target has been reached. The chase is complete.")
        elif wickets_lost >= 10 or legal_balls >= 120:
            st.warning("The standard chase has ended.")
        else:
            try:
                state = pd.DataFrame([build_state(team, target, runs_scored, wickets_lost, legal_balls)])
                prob = float(model.predict_proba(state)[0][1])
            except Exception as e:
                st.error(f"Prediction failed: {e}")
                st.stop()

            colour = ACCENT if prob >= 0.6 else WARN if prob >= 0.4 else BAD
            verdict = ("Chasing team is favoured 🔥" if prob >= 0.6
                       else "Evenly poised ⚖️" if prob >= 0.4
                       else "Defending team is ahead 🛡️")

            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob * 100,
                number=dict(suffix="%", font=dict(color=colour, size=48), valueformat=".1f"),
                title=dict(text=f"{team} chase-win probability", font=dict(size=15, color=MUTED)),
                gauge=dict(
                    axis=dict(range=[0, 100], tickcolor=MUTED),
                    bar=dict(color=colour, thickness=0.28),
                    bgcolor=CARD, borderwidth=0,
                    steps=[dict(range=[0, 40], color="#2A1F1E"),
                           dict(range=[40, 60], color="#2A2A1E"),
                           dict(range=[60, 100], color="#1E2A1E")],
                ),
            ))
            st.plotly_chart(style_chart(gauge, 290), use_container_width=True)
            st.markdown(f'<div class="verdict" style="color:{colour}">{verdict}</div>', unsafe_allow_html=True)

            balls_rem = 120 - legal_balls
            runs_rem = target - runs_scored
            req_rr = runs_rem * 6 / balls_rem
            cur_rr = runs_scored * 6 / legal_balls if legal_balls else 0

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Runs needed", runs_rem)
            m2.metric("Balls left", balls_rem)
            m3.metric("Required RR", f"{req_rr:.2f}")
            m4.metric("Current RR", f"{cur_rr:.2f}", delta=f"{cur_rr - req_rr:+.2f}")

    if go_btn and runs_scored < target and wickets_lost < 10 and legal_balls < 120:
        st.divider()
        st.subheader("📈 What-if: how wickets change the outlook")
        try:
            rows = pd.DataFrame([build_state(team, target, runs_scored, w, legal_balls) for w in range(0, 10)])
            probs = model.predict_proba(rows)[:, 1] * 100
            curve = pd.DataFrame({"wickets_lost": range(0, 10), "win_pct": probs})
            fig = px.line(curve, x="wickets_lost", y="win_pct", markers=True,
                          title="Win probability by wickets lost (same score & overs)")
            fig.update_traces(line=dict(color=ACCENT, width=3), marker=dict(size=8, color=ACCENT),
                              hovertemplate="%{x} wkts: %{y:.1f}%<extra></extra>")
            fig.add_vline(x=wickets_lost, line_dash="dash", line_color=WARN,
                          annotation_text="current", annotation_font_color=WARN)
            fig.update_xaxes(title="Wickets lost", dtick=1)
            fig.update_yaxes(title="Win %", range=[0, 100])
            st.plotly_chart(style_chart(fig, 330), use_container_width=True)
        except Exception:
            st.info("What-if curve is unavailable for this model input.")

        st.caption("Experimental estimate, not a guaranteed outcome. "
                   "Assumes a standard 120-ball innings and requires further validation.")