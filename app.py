# Flask Dashboard for College Event Feedback Analysis - Advanced UI Version with Theme and Background

from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly
import json
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from flask_bootstrap import Bootstrap
import os

# Initialize Flask app
app = Flask(__name__)
Bootstrap(app)

# Load dataset (already processed CSV)
data_path = os.path.join(os.path.dirname(__file__), 'final_event_feedback_analysis.csv')
df = pd.read_csv(data_path)

@app.route('/')
def index():
    # 📊 Top 3 Events
    top_events = df.groupby('Event_Name')['Avg_Score'].mean().sort_values(ascending=False).head(3).round(2)

    # 📈 Department-wise Satisfaction
    dept_avg = df.groupby('Department')['Avg_Score'].mean().sort_values(ascending=False).reset_index()
    dept_fig = px.bar(dept_avg, x='Department', y='Avg_Score', title='Department-wise Satisfaction',
                      color='Avg_Score', color_continuous_scale='Tealgrn')

    # 📉 Event Type vs Satisfaction
    event_type_fig = px.box(df, x='Event_Type', y='Avg_Score', points='all',
                            color='Event_Type', title='Event Type vs Satisfaction')

    # 📤 Sentiment Distribution
    sentiment_fig = px.histogram(df, x='Sentiment_Label', color='Sentiment_Label',
                                 title='Sentiment Distribution of Feedback Comments')

    # Get unique departments and event types for filters
    departments = ['All'] + sorted(df['Department'].dropna().unique().tolist())
    event_types = ['All'] + sorted(df['Event_Type'].dropna().unique().tolist())

    return render_template("dashboard.html",
                           top_events=top_events.to_dict(),
                           dept_graph=plotly.io.to_json(dept_fig),
                           type_graph=plotly.io.to_json(event_type_fig),
                           sentiment_graph=plotly.io.to_json(sentiment_fig),
                           departments=departments,
                           event_types=event_types)

@app.route('/filter', methods=['POST'])
def filter_data():
    department = request.form.get('department')
    event_type = request.form.get('event_type')

    filtered_df = df.copy()
    if department and department != "All":
        filtered_df = filtered_df[filtered_df['Department'] == department]
    if event_type and event_type != "All":
        filtered_df = filtered_df[filtered_df['Event_Type'] == event_type]

    # Filtered Department Chart
    dept_avg = filtered_df.groupby('Department')['Avg_Score'].mean().sort_values(ascending=False).reset_index()
    dept_fig = px.bar(dept_avg, x='Department', y='Avg_Score', title='Filtered Department-wise Satisfaction',
                      color='Avg_Score', color_continuous_scale='Mint')

    # Filtered Sentiment Chart
    sentiment_fig = px.histogram(filtered_df, x='Sentiment_Label', color='Sentiment_Label',
                                 title='Filtered Sentiment Distribution')

    return {
        'dept_graph': plotly.io.to_json(dept_fig),
        'sentiment_graph': plotly.io.to_json(sentiment_fig)
    }

if __name__ == '__main__':
    app.run(debug=True)
