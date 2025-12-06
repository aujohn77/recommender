# Amazon-style Product Recommendation System

A Python-based recommendation engine built on real Amazon review data. The system supports multiple collaborative filtering and matrix-factorisation models, and delivers fast, on-demand product recommendations via a Streamlit interface.

---

## ⚙️ Project Overview

This repository implements a full recommendation pipeline using a real-world dataset of Amazon product reviews. Its purpose is to produce relevant, personalized product suggestions — improving user engagement by capturing user behaviour and preferences.  

Key steps in the pipeline:

- **Data cleaning & preprocessing** — handle duplicates, missing values and sparsity; analyse user/item activity and address cold-start via minimum rating thresholds.  
- **Exploratory data analysis** — examine distributions of reviews per user and per product; detect activity patterns and sparsity.  
- **Model experiments & evaluation** — implement multiple recommendation strategies; evaluate performance using ranking metrics.  
- **Deployment-ready predictions** — precompute recommendation results so that the system can deliver fast suggestions through a Streamlit app.

---

## 📚 Models & Methods Implemented

| Method / Strategy | Description |
|------------------|-------------|
| Popularity-based ranking | Recommend globally popular products (rank-based) |
| Collaborative filtering (user/item-based) | Neighbourhood-based methods using tuned similarity metrics |
| Matrix factorisation (SVD) | Latent-factor model using SVD for compact representation |
| Hybrid approach | Combines strengths of collaborative filtering and matrix factorisation |

---

## ✅ Model Evaluation & Selection

All models are compared using **precision@k** and **recall@k** — ensuring performance is assessed based on recommendation relevance and coverage across users. The final production-ready solution uses **precomputed predictions**, enabling rapid inference via a lightweight web interface.

---

## 🚀 Tech Stack & Dependencies

- Python  
- Pandas  
- NumPy  
- Scikit-learn  
- Surprise  
- Matplotlib  
- Streamlit  
- gdown  
- Pickle  

---

## 🧪 How to Run Locally

1. Clone the repository  
   ```bash
   git clone https://github.com/aujohn77/recommender.git
   cd recommender
