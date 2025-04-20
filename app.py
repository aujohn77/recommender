import streamlit as st
import pandas as pd
import pickle
import os
from recommender_functions import get_top_n_products


with open("recommendations_dict.pkl", "rb") as f:
    recommendations_dict = pickle.load(f)

# Load recommendations dictionary
with open("recommendations_dict.pkl", "rb") as f:
    recommendations_dict = pickle.load(f)

# Load user mapping
with open("user_mapping.pkl", "rb") as f:
    user_mapping = pickle.load(f)

# Load product_stats (for fallback)
with open("product_stats.pkl", "rb") as f:
    product_stats = pickle.load(f)

# Preload example users
sample_user_ids = list(user_mapping.keys())[:10]

# Function to get recommendations from precomputed dictionary
def get_recommendations_from_dict(recommendations_dict, user_mapping, user_number):
    if user_number not in user_mapping:
        return f"Invalid user number. Choose between 1 and {len(user_mapping)}."

    user_id = user_mapping[user_number]
    return recommendations_dict.get(user_id, [])

# ---------------- Streamlit UI ---------------- #
st.title("📦 Product Recommender")

mode = st.sidebar.radio("Choose an option:", ["Demo User", "Enter User ID", "Continue as Guest"])

if mode == "Demo User":
    demo_user = st.selectbox("Select a demo user:", sample_user_ids)
    if st.button("Show Recommendations"):
        results = get_recommendations_from_dict(recommendations_dict, user_mapping, demo_user)
        st.success(f"Top recommendations for user #{demo_user}")
        st.table(pd.DataFrame(results, columns=["Product ID", "Adjusted Score"]))

elif mode == "Enter User ID":
    input_user = st.text_input(f"Enter User Number (0 to {len(user_mapping)-1}):")
    if st.button("Show Recommendations"):
        try:
            input_user_num = int(input_user)
            if input_user_num not in user_mapping:
                raise ValueError("Invalid user number.")
            results = get_recommendations_from_dict(recommendations_dict, user_mapping, input_user_num)
            st.success(f"Top personalized recommendations for user #{input_user}")

            # Convert to DataFrame
            rec_df = pd.DataFrame(results, columns=["product_id", "adjusted_average_rating"])
            
            # Merge with product_stats to get avg rating and count
            final_df = pd.merge(rec_df, product_stats, on="product_id", how="left")
            
            # Select and reorder columns
            final_df = final_df[["product_id", "average_rating", "rating_count", "adjusted_average_rating"]]
            
            # Round values for display
            final_df[["average_rating", "adjusted_average_rating"]] = final_df[["average_rating", "adjusted_average_rating"]].round(4)
            
            # Show in Streamlit
            st.table(final_df)


        
        except:
            st.warning("User not found. Showing top-ranked products.")
            results = get_top_n_products(product_stats, n=10, min_ratings=20)
            st.table(results)

else:
    if st.button("Show Popular Products"):
        results = get_top_n_products(product_stats, n=10, min_ratings=20)
        st.success("Popular picks based on adjusted average rating:")
        st.table(results)
