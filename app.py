import streamlit as st
import pandas as pd
import pickle
import os
from recommender_functions import get_top_n_products

# ————— Load Precomputed Data —————

# 1) Recommendations dictionary
with open("recommendations_dict.pkl", "rb") as f:
    recommendations_dict = pickle.load(f)

# 2) User mapping (frontend number → real user_id)
with open("user_mapping.pkl", "rb") as f:
    user_mapping = pickle.load(f)

# 3) Trim mapping to only users with entries in recommendations_dict
user_mapping = {
    num: uid
    for num, uid in user_mapping.items()
    if uid in recommendations_dict
}

# 4) Product stats for fallback
with open("product_stats.pkl", "rb") as f:
    product_stats = pickle.load(f)

# Preload a few example users for the “Demo User” mode
sample_user_ids = list(user_mapping.keys())[:10]


# ————— Helper Function —————

def get_recommendations_from_dict(recommendations_dict, user_mapping, user_number):
    """
    Returns a list of (product_id, adjusted_score) for a valid user_number,
    or an error string if the user_number is invalid.
    """
    if user_number not in user_mapping:
        return f"Invalid user number. Choose between {min(user_mapping)} and {max(user_mapping)}."

    user_id = user_mapping[user_number]
    return recommendations_dict.get(user_id, [])


# ————— Streamlit App —————

st.title("📦 Product Recommender")

mode = st.sidebar.radio(
    "Choose an option:",
    ["Demo User", "Enter User ID", "Continue as Guest"]
)

if mode == "Demo User":
    demo_user = st.selectbox("Select a demo user:", sample_user_ids)
    if st.button("Show Recommendations"):
        recs = get_recommendations_from_dict(
            recommendations_dict, user_mapping, demo_user
        )
        st.success(f"Top recommendations for user #{demo_user}")
        st.table(
            pd.DataFrame(recs, columns=["Product ID", "Adjusted Score"])
        )


elif mode == "Enter User ID":
    input_user = st.text_input(f"Enter User Number ({min(user_mapping)} to {max(user_mapping)}):")
    if st.button("Show Recommendations"):
        try:
            num = int(input_user)
            recs = get_recommendations_from_dict(recommendations_dict, user_mapping, num)

            if isinstance(recs, str) or not recs:
                st.warning("User not found or no recommendations. Showing top-ranked products.")
                fallback = get_top_n_products(product_stats, n=10, min_ratings=20)
                st.table(fallback)

            else:
                st.success(f"Top personalized recommendations for user #{num}")

                # recs is a list of (product_id, user_adjusted_score) tuples
                product_ids = [pid for (pid, _) in recs]

                # Filter product_stats to just these products
                final_df = product_stats[
                    product_stats['product_id'].isin(product_ids)
                ].copy()

                # Sort by the global adjusted average rating
                final_df = final_df.sort_values(
                    by='adjusted_average_rating',
                    ascending=False
                ).reset_index(drop=True)

                # Round the numeric columns
                final_df[['average_rating', 'adjusted_average_rating']] = (
                    final_df[['average_rating', 'adjusted_average_rating']]
                    .round(4)
                )

                # Display only the columns you requested
                st.table(final_df[
                    ['product_id', 'average_rating', 'rating_count', 'adjusted_average_rating']
                ])

        except ValueError:
            st.warning("Invalid input. Please enter a valid user number.")
            fallback = get_top_n_products(product_stats, n=10, min_ratings=20)
            st.table(fallback)



else:  # Continue as Guest
    if st.button("Show Popular Products"):
        topn = get_top_n_products(product_stats, n=10, min_ratings=20)
        st.success("Popular picks based on adjusted average rating:")
        st.table(topn)
