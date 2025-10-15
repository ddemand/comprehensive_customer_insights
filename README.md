# comprehensive_customer_insights
A merge of the NPS and customer churn to get the full picture.

# Dependencies
pip install pandas scikit-learn faker python-ulid reportlab scipy

# Workflow
1. Run the 'survey_data.py' to create a synthetic dataset of customer response records 
2. Execute the ‘churn_prediction_model.py’ script, which reads the ‘nps_data.csv’ and creates the churn prediction outcomes in the 'nps_data_with_churn_predictions.csv' file.
3. Execute the 'analyze_data.py' to create the final report.