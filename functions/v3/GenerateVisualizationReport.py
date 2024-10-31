import plotly
import json
from CreateInsightfulReport import lambda_handler


def create_visualization_report(chart_suggestion, visualization_data):
    # according to the suggestion, create a chart based on the data
    # chart suggestion might be pie chart, bar chart, line chart, histogram
    # visualization_data contain labels and values
    insight_results, chart_suggestions = lambda_handler(None, None)