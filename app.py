import streamlit as st
import pandas as pd
import numpy as np
import pickle

from recommender_functions import get_recommendations, get_top_n_products



# Load user mapping
with open("user_mapping.pkl", "rb") as f:
    user_mapping = pickle.load(f)

# Load user-item matrix
with open("user_item_matrix.pkl", "rb") as f:
    user_item_matrix = pickle.load(f)

# Load item counts
with open("item_counts.pkl", "rb") as f:
    item_counts = pickle.load(f)

# Load product_stats (for rank-based fallback)
with open("product_stats.pkl", "rb") as f:
    product_stats = pickle.load(f)

# Load your trained model
with open("algo_deploy.pkl", "rb") as f:
    algo_deploy = pickle.load(f)


# Assumed to already be loaded:
# - algo_deploy: trained model
# - user_item_matrix
# - user_mapping
# - item_counts
# - product_stats
# - get_recommendations(...)
# - get_top_n_products(...)

# Preload example users (in user_mapping)
sample_user_ids = list(user_mapping.keys())[:10]

st.title("📦 Product Recommender")

mode = st.sidebar.radio("Choose an option:", ["Demo User", "Enter User ID", "Continue as Guest"])

if mode == "Demo User":
    demo_user = st.selectbox("Select a demo user:", sample_user_ids)
    if st.button("Show Recommendations"):
        results = get_recommendations(
            user_item_matrix, user_mapping, demo_user,
            top_n=10, algo=algo_deploy, item_counts=item_counts
        )
        st.success(f"Top recommendations for user #{demo_user}")
        st.table(pd.DataFrame(results, columns=["Product ID", "Adjusted Score", "Rating Count"]))

elif mode == "Enter User ID":
    input_user = st.text_input("Enter User ID:")
    try:
        input_user_num = [k for k, v in user_mapping.items() if v == input_user][0]
        if st.button("Show Recommendations"):
            results = get_recommendations(
                user_item_matrix, user_mapping, input_user_num,
                top_n=10, algo=algo_deploy, item_counts=item_counts
            )
            st.success(f"Top personalized recommendations for user {input_user}")
            st.table(pd.DataFrame(results, columns=["Product ID", "Adjusted Score", "Rating Count"]))
    except:
        if st.button("Show Recommendations"):
            st.warning("User not found. Showing top-ranked products.")
            results = get_top_n_products(product_stats, n=10, min_ratings=20)
            st.table(results)

else:
    if st.button("Show Popular Products"):
        results = get_top_n_products(product_stats, n=10, min_ratings=20)
        st.success("Popular picks based on adjusted average rating:")
        st.table(results)
