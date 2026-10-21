# Student Dropout Risk Predictor

An early-warning tool that estimates which university students are at risk of dropping out, using only their **first 60 days** of activity, so that support can reach them while there is still time to help.

The project has two parts:
1. A **Jupyter/Colab notebook** that builds features, trains and compares three models, and evaluates them on students the models never saw.
2. A **Streamlit web app** that loads a trained model. It scores one student from a form, or ranks a whole CSV of students.

## How it works

- **Data:** Open University Learning Analytics Dataset (OULAD), 32,593 student records. A student whose final result is "Withdrawn" counts as a dropout.
- **Early prediction:** only activity up to day 60 is used. Students who had already left before day 60 are removed, which leaves 26,361 students (14.9% dropped out).
- **No data leakage:** the final result and the unregistration date are never given to the model as inputs.
- **Features:** online clicks (total, per half, per activity type, recent), active days, click trend (days 1-30 vs 31-60), assessments submitted and missed, average score, submission delay, and course background. The notebook uses 85 features. The web app uses a compact model with 10 inputs.
- **Models:** Logistic Regression (baseline), Random Forest (main model) and XGBoost.
- **Evaluation:** the notebook models use a 60/40 train/test split with stratification. The compact web app model is trained separately with a 70/30 split. Accuracy is misleading when only 15% of students drop out, so the models are judged by AUC and by how many real dropouts are reached when only the riskiest students are checked.

## Results

Notebook models, measured on 10,545 students they never saw:

| Model | AUC |
|---|---|
| Random Forest | 0.724 |
| Logistic Regression | 0.706 |
| XGBoost | 0.685 |

- Checking only the riskiest 20% of students reaches 43.9% of all dropouts with the Random Forest, and the riskiest 40% reaches 68.5%. Random guessing reaches about 20% and 40%.
- Adding activity-type features (85 features instead of about 60) gave about the same AUC as the simpler feature set, around 0.72.

What really happened to students in each risk group (High is the riskiest 10%, Medium the next 20%, Low the rest):

| Risk level | Notebook Random Forest (85 features) | Web app model (10 inputs, AUC 0.712, 7,909 unseen students) |
|---|---|---|
| High | 38.4% dropped out | 36.9% dropped out |
| Medium | 23.4% | 22.7% |
| Low | 9.1% | 9.6% |
| All students | 14.9% | 14.9% |

A High-risk label does not mean the student will drop out. About 6 in 10 High-risk students stayed. Use the result to decide who to support first.

## Project structure

```
dropout_web/
├── app.py                 # Web app: single student form
├── pages/
│   └── 1_Batch_Upload.py  # Web app: upload a CSV, get a ranked risk list
├── style.py               # Shared design for both pages
├── .streamlit/config.toml # Theme
├── dropout_model.joblib   # Trained model for the web app, created by the notebook
├── notebooks/
│   └── Student_Dropout_Prediction.ipynb
└── requirements.txt
```

## Run the web app locally

Requires Python 3.11 or newer.

```
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

On macOS or Linux, activate with `source venv/bin/activate`.

The model was saved with scikit-learn 1.6.1, and `requirements.txt` pins that version so the model loads correctly.

## Retrain the model

1. Download the dataset (link below) and open the notebook in Google Colab.
2. Upload the dataset zip file to Colab and run all cells. The notebook also needs `xgboost` and `matplotlib`, which Colab already has.
3. A cell near the end saves `dropout_model.joblib`. Replace the file in this folder with the new one.
4. Update the measured numbers at the top of `style.py` so the app's "How reliable is this tool?" section matches the new model.

## Limitations

- The model is trained on UK Open University students. It has not been validated on other institutions, including Indian colleges. To use it elsewhere, retrain it on that institution's own data.
- Ranking quality is moderate (AUC about 0.72). Predicting dropout at day 60 is hard, and predicting later is more accurate but leaves less time to act.
- The output is a risk estimate to support a counselor's judgement, not a final decision about a student.
- The warning-sign chips in the web app come from simple rules on the inputs. They are separate from the model's score.

## Data source

Kuzilek, J., Hlosta, M., Zdrahal, Z. (2017). Open University Learning Analytics Dataset. *Scientific Data* 4, 170171. Licensed under CC BY 4.0.

The dataset is not included in this repository. Download it from https://figshare.com/articles/OULAD_Open_University_Learning_Analytics_Dataset/5081998 or https://analyse.kmi.open.ac.uk/open_dataset.

## Built with

Python, pandas, scikit-learn, XGBoost, Streamlit, joblib.

## Author

Susmita Karmoker Saraboni, B.Tech Computer Science and Engineering, Brainware University.
