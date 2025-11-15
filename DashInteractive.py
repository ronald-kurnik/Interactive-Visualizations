# app.py
import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

# Generate sample dataset
np.random.seed(42)
n = 500
df = pd.DataFrame({
    'sales': np.random.exponential(1000, n),
    'profit': np.random.normal(200, 100, n),
    'region': np.random.choice(['North', 'South', 'East', 'West'], n),
    'category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books'], n),
    'date': pd.date_range('2024-01-01', periods=n, freq='D')
})
df['profit_margin'] = (df['profit'] / df['sales'].replace(0, 1)) * 100

# Use absolute value or shift negative margins for size
# Option: Use absolute margin for size, but color by sign
df['abs_margin'] = df['profit_margin'].abs()
df['margin_sign'] = np.where(df['profit_margin'] >= 0, 'Positive', 'Negative')

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

# Layout
app.layout = html.Div([
    html.H1("Interactive Sales Dashboard", style={'textAlign': 'center', 'color': '#2c3e50'}),

    html.Div([
        html.Div([
            html.Label("Select Region:"),
            dcc.Dropdown(
                id='region-dropdown',
                options=[{'label': r, 'value': r} for r in df['region'].unique()],
                value=df['region'].unique().tolist(),
                multi=True
            ),
        ], className="four columns"),

        html.Div([
            html.Label("Select Category:"),
            dcc.Dropdown(
                id='category-dropdown',
                options=[{'label': c, 'value': c} for c in df['category'].unique()],
                value=df['category'].unique().tolist(),
                multi=True
            ),
        ], className="four columns"),

        html.Div([
            html.Label("Sales Range:"),
            dcc.RangeSlider(
                id='sales-slider',
                min=df['sales'].min(),
                max=df['sales'].max(),
                value=[df['sales'].min(), df['sales'].max()],
                marks={int(df['sales'].quantile(0.25)): '25%',
                       int(df['sales'].median()): '50%',
                       int(df['sales'].quantile(0.75)): '75%'},
                tooltip={"placement": "bottom", "always_visible": True}
            ),
        ], className="four columns"),
    ], className="row", style={'marginBottom': 30}),

    html.Div([
        html.Div([
            dcc.Graph(id='scatter-plot')
        ], className="six columns"),

        html.Div([
            dcc.Graph(id='bar-chart')
        ], className="six columns"),
    ], className="row"),

    html.Div([
        dcc.Graph(id='line-chart')
    ], style={'marginTop': 30}),

    html.Footer([
        "Data: Simulated | Built with Plotly Dash",
        " • Negative margins shown in red (size = |margin|)"
    ], style={'textAlign': 'center', 'marginTop': 50, 'color': '#7f8c8d', 'fontStyle': 'italic'})
], style={'padding': '20px', 'fontFamily': 'Arial, sans-serif'})


# Callbacks
@app.callback(
    [Output('scatter-plot', 'figure'),
     Output('bar-chart', 'figure'),
     Output('line-chart', 'figure')],
    [Input('region-dropdown', 'value'),
     Input('category-dropdown', 'value'),
     Input('sales-slider', 'value')]
)
def update_charts(selected_regions, selected_categories, sales_range):
    filtered_df = df[
        df['region'].isin(selected_regions) &
        df['category'].isin(selected_categories) &
        (df['sales'] >= sales_range[0]) &
        (df['sales'] <= sales_range[1])
    ].copy()

    # --- SCATTER: Sales vs Profit (Size = |Profit Margin|) ---
    scatter_fig = px.scatter(
        filtered_df,
        x='sales', y='profit',
        color='margin_sign',  # Color by positive/negative
        size='abs_margin',    # Use absolute value for size
        hover_data=['region', 'date', 'profit_margin'],
        title='Sales vs Profit (Size = |Margin %|)',
        labels={'sales': 'Total Sales ($)', 'profit': 'Profit ($)'},
        color_discrete_map={'Positive': '#2ecc71', 'Negative': '#e74c3c'}
    )
    scatter_fig.update_traces(marker=dict(line=dict(width=1, color='white')))
    scatter_fig.update_layout(transition_duration=500, legend_title="Margin")

    # --- BAR: Average Profit by Region ---
    bar_data = filtered_df.groupby('region')['profit'].mean().reset_index()
    bar_fig = px.bar(
        bar_data, x='region', y='profit',
        color='region', title='Average Profit by Region',
        labels={'profit': 'Avg Profit ($)'},
        color_discrete_sequence=px.colors.qualitative.Plotly
    )

    # --- LINE: Sales Trend Over Time ---
    line_data = filtered_df.groupby('date')['sales'].sum().reset_index()
    line_fig = px.line(
        line_data, x='date', y='sales',
        title='Daily Sales Trend',
        labels={'sales': 'Total Sales ($)'},
        markers=True
    )
    line_fig.update_traces(line=dict(width=3, color='#3498db'))

    return scatter_fig, bar_fig, line_fig


# Run app
if __name__ == '__main__':
    app.run(debug=True)