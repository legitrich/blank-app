import requests
import streamlit as st
from datetime import date

# -----------------------------
# CONFIG
# -----------------------------
API_KEY = "YOUR_ODDS_API_KEY"   # Get from the-odds-api.com
SPORT = "americanfootball_nfl"
REGION = "us"

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
def american_odds_to_prob(odds):
    """Convert American odds to implied probability."""
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return -odds / (-odds + 100)

def get_odds():
    """Fetch odds from The Odds API."""
    url = f"https://api.the-odds-api.com/v4/sports/{SPORT}/odds"
    params = {"apiKey": API_KEY, "regions": REGION, "markets": "h2h,spreads,totals"}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []
    return response.json()

def parlay_probability(legs):
    """Multiply leg probabilities together."""
    prob = 1
    for p in legs:
        prob *= p
    return prob

# -----------------------------
# STREAMLIT APP
# -----------------------------
st.set_page_config(page_title="Parlay Agent", layout="wide")
st.title("🏈 Parlay Agent – Expert Betting Report")
st.write(f"📅 Report Date: {date.today()}")

# 1. Get Odds Data
odds_data = get_odds()

if not odds_data:
    st.error("⚠️ Could not fetch odds data. Check API key or plan limits.")
else:
    # 2. Expert Adjusted Probabilities (manual tweaks for now)
    expert_probs = {
        "Dallas Cowboys -2.5": 0.62,
        "Jets vs Patriots UNDER 44.5": 0.68,
        "Kansas City Chiefs ML": 0.74,
        "San Francisco 49ers -6.5": 0.59
    }

    # 3. Example implied probs from book (placeholder until mapped from odds API)
    book_probs = {
        "Dallas Cowboys -2.5": 0.52,
        "Jets vs Patriots UNDER 44.5": 0.52,
        "Kansas City Chiefs ML": 0.71,
        "San Francisco 49ers -6.5": 0.52
    }

    # 4. Display Expert Picks with EV Highlight
    st.subheader("🔥 Featured Expert Picks")
    good_legs = []  # store only +EV bets
    for pick, agent_prob in expert_probs.items():
        book_prob = book_probs[pick]
        edge = round((agent_prob - book_prob) * 100, 1)

        if agent_prob > book_prob:
            st.success(f"✅ {pick}: Agent {int(agent_prob*100)}% vs Book {int(book_prob*100)}% | Edge: +{edge}%")
            good_legs.append(pick)
        else:
            st.error(f"❌ {pick}: Agent {int(agent_prob*100)}% vs Book {int(book_prob*100)}% | Edge: {edge}%")

    # 5. Build Parlays from +EV Legs
    st.subheader("🎯 Recommended Parlays (Only +EV Legs)")

    if len(good_legs) < 2:
        st.warning("Not enough +EV legs to build a strong parlay today.")
    else:
        parlays = {
            "💎 Safe 3-Leg": good_legs[:3],
            "🚀 Aggressive All-Legs": good_legs
        }

        for name, legs in parlays.items():
            prob = parlay_probability([expert_probs[l] for l in legs])
            st.markdown(f"### {name}")
            st.write(f"Legs: {', '.join(legs)}")
            st.write(f"✅ Combined Probability: **{int(prob*100)}%**")
            st.write("---")

    # 6. Closing Notes
    st.subheader("🧾 Agent Summary")
    st.write("""
    - Green picks = bets where expert model beats sportsbook
    - Red picks = avoid (no edge or negative EV)
    - Parlays are only constructed from green (+EV) legs
    """)