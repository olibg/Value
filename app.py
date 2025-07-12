import streamlit as st
import requests

API_KEY = st.secrets["ODDS_API_KEY"]

@st.cache_data(ttl=300)
def get_odds(sport="soccer_epl", region="uk"):
    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds"
    params = {
        "apiKey": API_KEY,
        "regions": region,
        "markets": "h2h,spreads,totals",
        "oddsFormat": "decimal"
    }
    response = requests.get(url, params=params)
    return response.json()

def implied_prob(odds):
    return round(1 / odds, 4)

def expected_value(prob, odds):
    return round((prob * odds) - 1, 4)

def kelly(prob, odds, bankroll):
    b = odds - 1
    k = ((b * prob) - (1 - prob)) / b
    return round(max(0, k) * bankroll, 2)

st.title("⚽ Value Bet Finder - All Markets")

sport = st.selectbox("Choose a sport", ["soccer_epl", "soccer_uefa_european_championship", "basketball_nba"])
odds_data = get_odds(sport)

if not odds_data:
    st.error("Failed to load odds — check your API key or limits.")
else:
    for match in odds_data[:5]:
        st.subheader(f"{match['home_team']} vs {match['away_team']}")
        for bookmaker in match['bookmakers']:
            st.markdown(f"**Bookmaker:** {bookmaker['title']}")
            for market in bookmaker['markets']:
                st.markdown(f"**Market:** {market['key']} (last updated: {market['last_update']})")
                for outcome in market['outcomes']:
                    team = outcome['name']
                    odds = outcome['price']
                    prob = st.number_input(f"Your probability for {team} in market '{market['key']}'", min_value=0.0, max_value=1.0, step=0.01, key=f"{match['id']}_{team}_{market['key']}")
                    bankroll = st.number_input("Your Bankroll (£)", min_value=10.0, value=100.0, step=10.0, key=f"bankroll_{match['id']}_{team}_{market['key']}")
                    if prob > 0:
                        ip = implied_prob(odds)
                        ev = expected_value(prob, odds)
                        kelly_stake = kelly(prob, odds, bankroll)
                        st.write(f"Odds: {odds} | Implied Prob: {ip:.2%}")
                        st.write(f"Expected Value: {ev:.2f} → {'✅ Value Bet' if ev > 0 else '❌ Not a value bet'}")
                        st.write(f"Kelly Stake: £{kelly_stake}")
                        st.markdown("---")
