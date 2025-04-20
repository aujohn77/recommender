import streamlit as st
import pandas as pd
import numpy as np
import pickle
import os
import gdown
import requests
from recommender_functions import get_recommendations, get_top_n_products

# Download user_item_matrix.pkl if it doesn't exist
file_id = "1xBlXLWURaR6MuFIlZrnYWiMbj2sLxi6j"
output_path = "user_item_matrix.pkl"

if not os.path.exists(output_path):
    gdown.download(id=file_id, output=output_path, quiet=False)


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

# Preload example users (in user_mapping)
sample_user_ids = list(user_mapping.keys())[:10]





def call_prediction_api(user_id, product_id):
    try:
        response = requests.post(
            "https://aujohn77.hf.space/predict",
            json={"user_id": user_id, "product_id": product_id},
            timeout=5
        )
        result = response.json()
        return result.get("rating", None)
    except Exception as e:
        return None

# ✅ REPLACE get_recommendations with version that uses call_prediction_api
def get_recommendations(user_item_matrix, user_mapping, user_number, top_n, item_counts, threshold=4.0):
    if user_number not in user_mapping:
        return f"Invalid user number. Choose between 1 and {len(user_mapping)}."

    real_user_id = user_mapping[user_number]
    non_interacted_products = user_item_matrix.loc[real_user_id][user_item_matrix.loc[real_user_id].isnull()].index.tolist()

    recommendations = []
    for item_id in non_interacted_products:
        est = call_prediction_api(real_user_id, item_id)
        if est is None:
            continue

        n = item_counts.get(item_id, 1)
        adjusted_est = est - (1 / np.sqrt(n))

        if adjusted_est >= threshold:
            recommendations.append((item_id, adjusted_est, n))

    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)[:top_n]
    return recommendations






st.title("📦 Product Recommender")

mode = st.sidebar.radio("Choose an option:", ["Demo User", "Enter User ID", "Continue as Guest"])

if mode == "Demo User":
    demo_user = st.selectbox("Select a demo user:", sample_user_ids)
    if st.button("Show Recommendations"):
        results = get_recommendations(
        user_item_matrix, user_mapping, demo_user,
        top_n=10, item_counts=item_counts
        )

        st.success(f"Top recommendations for user #{demo_user}")
        st.table(pd.DataFrame(results, columns=["Product ID", "Adjusted Score", "Rating Count"]))



elif mode == "Enter User ID":
    input_user = st.text_input(f"Enter User Number (0 to {len(user_mapping)-1}):")
    if st.button("Show Recommendations"):
        try:
            input_user_num = int(input_user)
            if input_user_num not in user_mapping:
                raise ValueError("Invalid user number.")

            results = get_recommendations(
                user_item_matrix, user_mapping, input_user_num,
                top_n=10, item_counts=item_counts
            )
            st.success(f"Top personalized recommendations for user #{input_user}")
            st.table(pd.DataFrame(results, columns=["Product ID", "Adjusted Score", "Rating Count"]))
        except:
            st.warning("User not found. Showing top-ranked products.")
            results = get_top_n_products(product_stats, n=10, min_ratings=20)
            st.table(results)


else:
    if st.button("Show Popular Products"):
        results = get_top_n_products(product_stats, n=10, min_ratings=20)
        st.success("Popular picks based on adjusted average rating:")
        st.table(results)
