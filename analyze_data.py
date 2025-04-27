# ====== Analyze Data Using Grok3
# Purpose: Analyzes NPS data from nps_data.csv to produce an executive summary with Overall Customer Sentiment,
# Top 3 Strengths, Top 3 Opportunities, and Recommended Action, then generates a PDF report.

import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import json


# ====== Function to analyze NPS data
def analyze_nps_data(df):
    """
    Analyze NPS data and return a summary with overall sentiment, strengths, opportunities, and action.

    Args:
        df (pd.DataFrame): DataFrame with 'Customer Number', 'Order Number', 'NPS Score', 'Customer Response',
                           'Churned', 'Churn Reason'

    Returns:
        dict: Dictionary with 'summary', 'top_strengths', 'top_opportunities', 'recommended_action'
    """
    required_columns = ['Customer Number', 'Order Number', 'NPS Score', 'Customer Response', 'Churned', 'Churn Reason']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"DataFrame must contain {required_columns}")

    # Calculate NPS score distribution
    nps_summary = df['NPS Score'].value_counts().sort_index().to_dict()
    total_responses = len(df)
    promoter_pct = ((nps_summary.get(1, 0) + nps_summary.get(2, 0)) / total_responses * 100) if total_responses else 0
    detractor_pct = ((nps_summary.get(4, 0) + nps_summary.get(5, 0)) / total_responses * 100) if total_responses else 0
    neutral_pct = (nps_summary.get(3, 0) / total_responses * 100) if total_responses else 0

    # Calculate churn rate
    churn_rate = (df['Churned'].sum() / total_responses * 100) if total_responses else 0

    # Overall Customer Sentiment
    if promoter_pct > detractor_pct + 20:
        sentiment = "Customer sentiment is strongly positive, with a high proportion of promoters (NPS 1-2) and low churn."
    elif detractor_pct > promoter_pct + 20:
        sentiment = "Customer sentiment is concerning, with a high proportion of detractors (NPS 4-5) and notable churn."
    else:
        sentiment = "Customer sentiment is mixed, with a balance of promoters, neutrals, and detractors, indicating areas for improvement."

    # Top 3 Strengths (based on NPS 1-2)
    positive_comments = df[df['NPS Score'].isin([1, 2])]['Customer Response'].str.split(' and ').explode()
    positive_counts = positive_comments.value_counts().head(3)
    top_strengths = [
        {"reason": comment.strip('.'), "description": f"Mentioned in {count} responses"}
        for comment, count in positive_counts.items()
    ]

    # Top 3 Opportunities (based on NPS 4-5 and churn reasons)
    negative_comments = df[df['NPS Score'].isin([4, 5])]['Customer Response'].str.split(' and ').explode()
    churn_reasons = df[df['Churned'] == 1]['Churn Reason']
    combined_issues = pd.concat([negative_comments, churn_reasons]).value_counts().head(3)
    top_opportunities = [
        {"reason": issue, "description": f"Reported in {count} instances, contributing to dissatisfaction and churn"}
        for issue, count in combined_issues.items()
    ]

    # Recommended Action
    if top_opportunities:
        primary_issue = top_opportunities[0]['reason']
        if "pricing" in primary_issue.lower():
            action = "Implement transparent pricing policies and eliminate hidden fees to rebuild trust and reduce churn."
        elif "customer service" in primary_issue.lower():
            action = "Invest in staff training to improve customer service responsiveness and expertise, addressing key dissatisfaction drivers."
        elif "product availability" in primary_issue.lower() or "stock" in primary_issue.lower():
            action = "Enhance inventory management to ensure consistent product availability, meeting customer expectations."
        elif "shipping" in primary_issue.lower() or "delivery" in primary_issue.lower():
            action = "Optimize shipping processes and provide real-time order tracking to improve delivery reliability."
        else:
            action = "Address key customer pain points by reviewing feedback and implementing targeted improvements to stay competitive."
    else:
        action = "Continue leveraging strengths while monitoring feedback to maintain industry leadership."

    result = {
        "summary": {
            "overall_sentiment": sentiment,
            "promoter_percentage": f"{promoter_pct:.1f}%",
            "neutral_percentage": f"{neutral_pct:.1f}%",
            "detractor_percentage": f"{detractor_pct:.1f}%",
            "churn_rate": f"{churn_rate:.1f}%"
        },
        "top_strengths": top_strengths,
        "top_opportunities": top_opportunities,
        "recommended_action": action
    }
    return result


# ====== Function to assign Action column
def assign_action_column(df):
    """
    Assign 'Action' column based on NPS score.

    Args:
        df (pd.DataFrame): Original DataFrame with 'NPS Score'

    Returns:
        pd.DataFrame: DataFrame with new 'Action' column
    """
    df['Action'] = 'No'
    df.loc[df['NPS Score'].isin([4, 5]), 'Action'] = 'Yes'
    return df


# ====== Function to generate PDF report
def generate_pdf_report(result, output_path="nps_executive_summary.pdf"):
    """
    Generate a PDF report with the executive summary.

    Args:
        result (dict): Dictionary with 'summary', 'top_strengths', 'top_opportunities', 'recommended_action'
        output_path (str): Path to save the PDF file
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, spaceAfter=20, textColor=colors.black)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=14, spaceBefore=12, spaceAfter=10,
                                   textColor=colors.darkgray)
    body_style = ParagraphStyle('Body', parent=styles['BodyText'], fontSize=12, spaceAfter=8)

    story = []
    story.append(Paragraph("Executive Customer Sentiment Summary", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y')}", body_style))
    story.append(Spacer(1, 12))

    # Overall Customer Sentiment
    story.append(Paragraph("Overall Customer Sentiment", heading_style))
    summary = result.get('summary', {})
    sentiment_text = summary.get('overall_sentiment', 'No sentiment provided')
    metrics = (f"Promoters (NPS 1-2): {summary.get('promoter_percentage', 'N/A')}, "
               f"Neutrals (NPS 3): {summary.get('neutral_percentage', 'N/A')}, "
               f"Detractors (NPS 4-5): {summary.get('detractor_percentage', 'N/A')}, "
               f"Churn Rate: {summary.get('churn_rate', 'N/A')}")
    story.append(Paragraph(sentiment_text, body_style))
    story.append(Paragraph(metrics, body_style))
    story.append(Spacer(1, 12))

    # Top 3 Strengths
    story.append(Paragraph("Top 3 Strengths", heading_style))
    for i, item in enumerate(result.get('top_strengths', [])[:3], 1):
        reason = item.get('reason', 'Unknown strength')
        description = item.get('description', '')
        text = f"{i}. <b>{reason}</b>: {description}"
        story.append(Paragraph(text, body_style))
    story.append(Spacer(1, 12))

    # Top 3 Opportunities
    story.append(Paragraph("Top 3 Opportunities", heading_style))
    for i, item in enumerate(result.get('top_opportunities', [])[:3], 1):
        reason = item.get('reason', 'Unknown issue')
        description = item.get('description', '')
        text = f"{i}. <b>{reason}</b>: {description}"
        story.append(Paragraph(text, body_style))
    story.append(Spacer(1, 12))

    # Recommended Action
    story.append(Paragraph("Recommended Action", heading_style))
    action = result.get('recommended_action', 'No action provided')
    story.append(Paragraph(action, body_style))

    try:
        doc.build(story)
        print(f"PDF report saved to: {output_path}")
    except Exception as e:
        print(f"Error generating PDF: {e}")


# ====== Main execution
try:
    # Load the original DataFrame
    df = pd.read_csv('nps_data.csv')

    # Create a filtered DataFrame for analysis
    filtered_df = df[['Customer Number', 'Order Number', 'NPS Score', 'Customer Response', 'Churned', 'Churn Reason']]

    # Analyze the data
    result = analyze_nps_data(filtered_df)

    # Assign 'Action' column to the original DataFrame
    df = assign_action_column(df)

    # Print results
    print("Overall Customer Sentiment:")
    print(result['summary']['overall_sentiment'])
    print(f"Promoters: {result['summary']['promoter_percentage']}, "
          f"Neutrals: {result['summary']['neutral_percentage']}, "
          f"Detractors: {result['summary']['detractor_percentage']}, "
          f"Churn Rate: {result['summary']['churn_rate']}")
    print("\nTop 3 Strengths:")
    for i, strength in enumerate(result['top_strengths'], 1):
        print(f"{i}. {strength['reason']} ({strength['description']})")
    print("\nTop 3 Opportunities:")
    for i, opportunity in enumerate(result['top_opportunities'], 1):
        print(f"{i}. {opportunity['reason']} ({opportunity['description']})")
    print("\nRecommended Action:")
    print(result['recommended_action'])

    # Generate PDF report
    generate_pdf_report(result)

    # Save the updated DataFrame with Action column
    df.to_csv('nps_data_with_results.csv', index=False)
    print("Updated data saved to 'nps_data_with_results.csv'")

except FileNotFoundError:
    print("Error: 'nps_data.csv' not found.")
except Exception as e:
    print(f"Error during analysis or processing: {e}")