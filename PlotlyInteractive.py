import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Generate sample data
np.random.seed(42)
df = pd.DataFrame({
    'x': np.random.randn(100),
    'y': np.random.randn(100),
    'category': np.random.choice(['A', 'B', 'C'], 100),
    'size': np.random.rand(100) * 30 + 10
})

# Create interactive scatter plot with Plotly Express
fig = px.scatter(
    df, 
    x='x', 
    y='y',
    color='category',
    size='size',
    hover_data=['x', 'y'],
    title='Interactive Scatter Plot with Plotly',
    labels={'x': 'X Axis', 'y': 'Y Axis'},
    template='plotly_dark'
)

# Enhance layout
fig.update_layout(
    hovermode='closest',
    showlegend=True,
    height=600
)

# Add interactive features
fig.update_traces(
    marker=dict(line=dict(width=1, color='white')),
    selector=dict(mode='markers')
)

# Show the plot
fig.show()

# Optional: Save as HTML for sharing
fig.write_html("interactive_scatter_plot.html")