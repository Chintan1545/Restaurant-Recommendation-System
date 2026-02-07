import streamlit as st
import requests
import pandas as pd

# ---------------- CONFIG ----------------
API_URL = "http://127.0.0.1:8000/search"

st.set_page_config(
    page_title="Restaurant Recommendation System",
    layout="wide"
)

st.title("🍽️ Restaurant Recommendation System")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    return pd.read_csv("food1.csv")

df = load_data()

# ---------------- PREPARE DROPDOWNS ----------------
# Extract unique cuisines
all_cuisines = set()
for c in df["cuisines"].dropna():
    for cuisine in c.split(","):
        all_cuisines.add(cuisine.strip())

cuisine_options = sorted(list(all_cuisines))
locality_options = sorted(df["locality"].dropna().unique())

# ---------------- SEARCH FORM ----------------
with st.form("search_form"):
    col1, col2, col3 = st.columns(3)

    with col1:
        people = st.number_input(
            "👥 Number of People",
            min_value=1,
            value=2
        )

    with col2:
        min_price = st.number_input(
            "💰 Minimum Budget",
            min_value=0,
            value=200
        )

    with col3:
        max_price = st.number_input(
            "💸 Maximum Budget",
            min_value=0,
            value=1000
        )

    col4, col5 = st.columns(2)

    with col4:
        cuisine = st.selectbox(
            "🍴 Select Cuisine",
            cuisine_options,
            index=cuisine_options.index("North Indian") if "North Indian" in cuisine_options else 0
        )

    with col5:
        locality = st.selectbox(
            "📍 Select Locality",
            locality_options,
            index=locality_options.index("Alambagh") if "Alambagh" in locality_options else 0
        )

    submit = st.form_submit_button("🔍 Find Restaurants")

# ---------------- API CALL ----------------
if submit:
    payload = {
        "people": people,
        "min_price": min_price,
        "max_price": max_price,
        "cuisine": cuisine,
        "locality": locality
    }

    with st.spinner("Finding best restaurants for you... 🍽️"):
        try:
            response = requests.post(API_URL, json=payload)

            if response.status_code == 200:
                restaurants = response.json().get("restaurants", [])

                if not restaurants:
                    st.warning("No restaurants found 😕")
                else:
                    st.success(f"Found {len(restaurants)} restaurants 🎉")

                    for r in restaurants:
                        st.markdown(f"### 🍽️ {r['name']}")
                        st.write(f"📍 **Address:** {r['address']}")
                        st.write(f"🍴 **Cuisines:** {r['cuisines']}")
                        st.write(f"⭐ **Rating:** {r['aggregate_rating']}")
                        st.write(f"⏰ **Timings:** {r['timings']}")
                        st.markdown(f"[🔗 Visit Restaurant]({r['url']})")
                        st.divider()

            else:
                st.error("API error. Please try again later.")

        except Exception as e:
            st.error(f"Could not connect to backend: {e}")
