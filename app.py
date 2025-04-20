import streamlit as st
import pandas as pd
import pickle
import os
from recommender_functions import get_top_n_products

# ————— Load Precomputed Data —————
with open("recommendations_dict.pkl", "rb") as f:
    recommendations_dict = pickle.load(f)  # top‑N recs per user

with open("user_mapping.pkl", "rb") as f:
    user_mapping = pickle.load(f)  # front‑end ID → real user_id

# keep only users who actually have precomputed recommendations
user_mapping = {
    num: uid
    for num, uid in user_mapping.items()
    if uid in recommendations_dict
}

with open("product_stats.pkl", "rb") as f:
    product_stats = pickle.load(f)  # stats for fallback

sample_user_ids = list(user_mapping.keys())[:10]  # demo users

# ————— Helper Function —————
def get_recommendations_from_dict(recommendations_dict, user_mapping, user_number):
    if user_number not in user_mapping:
        return []  # invalid user
    return recommendations_dict.get(user_mapping[user_number], [])

# ————— Streamlit App —————
st.title("📦 Product Recommender")

# center the mode selector under the title
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    mode = st.radio(
        "Choose a recommendation mode:",
        ["🎯 Active User (personalized)", "👋 New User (popular products)"],
        horizontal=True  # show options side by side
    )

# — Personalized Mode for Active Users ——
if mode == "🎯 Active User (personalized)":
    input_user_num = st.selectbox(
        "Select User Number",
        options=list(user_mapping.keys()),
        format_func=lambda x: f"{x} → {user_mapping[x]}"  # show mapping
    )
    if st.button("Show Recommendations"):
        recs = get_recommendations_from_dict(
            recommendations_dict, user_mapping, input_user_num
        )  # fetch from dict

        if not recs:
            # fallback for no recs
            st.warning("No personalized recommendations found. Showing top‑ranked products.")
            topn = get_top_n_products(product_stats, n=10, min_ratings=20)
            topn = topn[['product_id', 'rating_count', 'adjusted_average_rating']]
            st.table(topn)

        else:
            # display personalized recommendations
            st.success(f"Top personalized recommendations for user #{input_user_num}")
            product_ids = [pid for pid, _ in recs]
            final_df = (
                product_stats[product_stats['product_id'].isin(product_ids)]
                .sort_values('adjusted_average_rating', ascending=False)
                .reset_index(drop=True)
            )
            final_df = final_df[['product_id', 'rating_count', 'adjusted_average_rating']]
            final_df['adjusted_average_rating'] = final_df['adjusted_average_rating'].round(4)
            st.table(final_df)

# — Fallback Mode for New/Cold‑start Users ——
else:
    if st.button("Show Popular Products"):
        topn = get_top_n_products(product_stats, n=10, min_ratings=20)
        topn = topn[['product_id', 'rating_count', 'adjusted_average_rating']]
        st.success("Popular picks based on adjusted average rating:")
        st.table(topn)
