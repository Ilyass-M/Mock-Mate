# 🧠 Hiring Decision Predictor using Decision Tree

This project uses a Decision Tree Classifier to predict hiring decisions based on a candidate’s CV match score and a weighted evaluation score. The model is trained on a fixed dataset and can also be used to make predictions on new candidates.

---

## Demo Video

[Click here to watch the demo video](https://drive.google.com/file/d/1arGl-sGutiDcfyHwaKpquhHS9FtTa28r/view?usp=sharing)

## 🚀 Features

- Train a Decision Tree model using a structured dataset.
- Predict whether a new candidate should be hired or not.
- View human-readable decision rules derived from the tree.
- Integrate new candidate evaluations dynamically from `questions_df`.

---

## 📊 Dataset

A fixed dataset of 20 candidates is used for training:

- `candidate_id`: Unique identifier for each candidate.
- `cv_match_score`: Score reflecting how well a candidate’s CV matches the job description.
- `weighted_score`: Aggregated evaluation score (e.g., quiz or assessment).
- `hire_decision`: 1 = Hire, 0 = Not Hire.

---

## 🧠 How It Works

1. **Train the Model**  
   - The decision tree is trained with a max depth of 3 for simplicity and interpretability.
   - The dataset is split into training and testing sets.
   - Model accuracy is printed on the test set.

2. **Make Predictions**  
   - The average `cv_match_score` and `weighted_score` are calculated from a sample DataFrame (`questions_df`).
   - These scores are used as input to predict if a new candidate should be hired.
   - The model outputs a prediction and class probabilities.

---

## 🛠️ Setup Instructions

1. **Install Requirements**

```bash
pip install pandas scikit-learn
