import numpy as np



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
