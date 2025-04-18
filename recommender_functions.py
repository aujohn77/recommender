import numpy as np

def get_recommendations(user_item_matrix, user_mapping, user_number, top_n, algo, item_counts, threshold=4.0):
    """
    Recommend top_n products for a given user_number using adjusted predictions.

    Adjustment: predicted_rating - 1/sqrt(n), where n = number of ratings for the product.
    Only products with adjusted prediction >= threshold will be recommended.

    Parameters:
        user_item_matrix (DataFrame) : user-product interaction matrix
        user_mapping (dict)          : mapping from user_number to real user_id
        user_number (int)            : user chosen by frontend (e.g., 1, 2, 3...)
        top_n (int)                  : number of products to recommend
        algo                         : trained recommendation model (SVD, KNN, etc.)
        item_counts (dict)           : dictionary with product_id as key and rating count as value
        threshold (float)            : minimum adjusted rating to consider a product recommendable

    Returns:
        List of tuples: (product_id, adjusted_predicted_rating, rating_count)
    """

    # Check if user_number is valid
    if user_number not in user_mapping:
        return f'Invalid user number. Choose between 1 and {len(user_mapping)}.'

    # Map user_number to actual user_id
    real_user_id = user_mapping[user_number]

    # Get products this user hasn't rated yet
    non_interacted_products = user_item_matrix.loc[real_user_id][
        user_item_matrix.loc[real_user_id].isnull()
    ].index.tolist()

    # Predict and adjust ratings
    recommendations = []
    for item_id in non_interacted_products:
        est = algo.predict(real_user_id, item_id).est
        n = item_counts.get(item_id, 1)
        adjusted_est = est - (1 / np.sqrt(n))

        # Filter: Only keep products with adjusted score >= threshold
        if adjusted_est >= threshold:
            recommendations.append((item_id, adjusted_est, n))

    # Sort and return top_n recommendations
    recommendations = sorted(recommendations, key=lambda x: x[1], reverse=True)[:top_n]
    return recommendations


def get_top_n_products(df, n=10, min_ratings=2):
    """
    Returns top n product_ids with highest average ratings,
    considering only products with more than min_ratings interactions.
    """
    top_products = (
        df[df['rating_count'] > min_ratings]
        .sort_values('adjusted_average_rating', ascending=False)
        .head(n)
    )
    return top_products[['product_id', 'average_rating', 'rating_count', 'adjusted_average_rating']]