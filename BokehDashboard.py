# app.py
from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, HoverTool, MultiChoice, RangeSlider,
    Tabs, TabPanel, DataTable, TableColumn, DateFormatter, NumberFormatter
)
from bokeh.layouts import column, row
import pandas as pd
import numpy as np

# ------------------------------------------------------------------
# 1. Generate sample data (no deprecation warnings)
# ------------------------------------------------------------------
np.random.seed(42)
n = 1000
df = pd.DataFrame({
    'sales': np.random.exponential(800, n),
    'profit': np.random.normal(180, 120, n),
    'region': np.random.choice(['North', 'South', 'East', 'West'], n),
    'category': np.random.choice(['Electronics', 'Clothing', 'Food', 'Books'], n),
    'date': pd.date_range('2024-01-01', periods=n, freq='12h')   # <-- lowercase 'h'
})
df['profit_margin'] = (df['profit'] / df['sales'].replace(0, 1)) * 100
df['abs_margin']   = df['profit_margin'].abs()
df['color']        = np.where(df['profit_margin'] >= 0, '#2ecc71', '#e74c3c')
df['size']         = df['abs_margin'].clip(lower=5, upper=40)   # pixel size

# ------------------------------------------------------------------
# 2. Sources
# ------------------------------------------------------------------
scatter_source = ColumnDataSource(df)

# Line chart – aggregate on the fly in the callback
line_source = ColumnDataSource(data=dict(date=[], sales=[]))

# Bar chart – aggregate on the fly
bar_source = ColumnDataSource(data=dict(category=[], profit=[]))

# ------------------------------------------------------------------
# 3. Plots
# ------------------------------------------------------------------

# ---- Scatter -------------------------------------------------------
scatter = figure(
    title="Sales vs Profit (Size = |Margin %|)",
    x_axis_label="Sales ($)", y_axis_label="Profit ($)",
    height=420, width=620,
    tools="pan,wheel_zoom,box_zoom,reset,save"
)

# Use scatter() instead of circle()
scatter.scatter(
    x='sales', y='profit',
    size='size', color='color', alpha=0.7,
    source=scatter_source, legend_field='region'
)

scatter.add_tools(HoverTool(tooltips=[
    ("Sales",   "@sales{$0,0.00}"),
    ("Profit",  "@profit{$0,0.00}"),
    ("Margin %","@{profit_margin}{0.0}"),
    ("Region",  "@region"),
    ("Category","@category"),
    ("Date",    "@date{%F %H:%M}")
], formatters={'@date': 'datetime'}))

# ---- Line (daily sales) --------------------------------------------
line_fig = figure(
    title="Daily Sales Trend",
    x_axis_type='datetime', x_axis_label="Date", y_axis_label="Total Sales ($)",
    height=300, width=900,
    tools="pan,wheel_zoom,box_zoom,reset"
)

line_fig.line('date', 'sales', source=line_source, line_width=3, color='#3498db')
line_fig.scatter('date', 'sales', source=line_source, size=6, color='#2980b9')

# ---- Bar (avg profit by category) ----------------------------------
bar_fig = figure(
    x_range=[], title="Average Profit by Category",
    height=300, width=400, tools=""
)
bars = bar_fig.vbar(x='category', top='profit', width=0.6,
                    source=bar_source, line_color="white", fill_color="#9b59b6")
bar_fig.xgrid.grid_line_color = None
bar_fig.y_range.start = 0

# ------------------------------------------------------------------
# 4. Controls
# ------------------------------------------------------------------
region_ctrl = MultiChoice(
    title="Regions",
    value=list(df['region'].unique()),
    options=[(r, r) for r in df['region'].unique()]
)

cat_ctrl = MultiChoice(
    title="Categories",
    value=list(df['category'].unique()),
    options=[(c, c) for c in df['category'].unique()]
)

sales_ctrl = RangeSlider(
    title="Sales Range ($)",
    start=df['sales'].min(), end=df['sales'].max(),
    value=(df['sales'].min(), df['sales'].max()),
    step=10
)

# ------------------------------------------------------------------
# 5. Data Table
# ------------------------------------------------------------------
table_cols = [
    TableColumn(field="date",          title="Date",      formatter=DateFormatter(format="%Y-%m-%d %H:%M")),
    TableColumn(field="sales",        title="Sales ($)", formatter=NumberFormatter(format="$0,0.00")),
    TableColumn(field="profit",       title="Profit ($)",formatter=NumberFormatter(format="$0,0.00")),
    TableColumn(field="profit_margin",title="Margin %",  formatter=NumberFormatter(format="0.0")),
    TableColumn(field="region",       title="Region"),
    TableColumn(field="category",     title="Category"),
]
data_table = DataTable(source=scatter_source, columns=table_cols, height=300, width=900)

# ------------------------------------------------------------------
# 6. Callback – updates everything when filters change
# ------------------------------------------------------------------
def update_all():
    # ---- Filter ----------------------------------------------------
    mask = (
        df['region'].isin(region_ctrl.value) &
        df['category'].isin(cat_ctrl.value) &
        (df['sales'] >= sales_ctrl.value[0]) &
        (df['sales'] <= sales_ctrl.value[1])
    )
    filtered = df[mask].copy()
    filtered['size'] = filtered['abs_margin'].clip(5, 40)

    # ---- Scatter & Table -------------------------------------------
    scatter_source.data = filtered

    # ---- Line chart ------------------------------------------------
    line_agg = (
        filtered.groupby(pd.Grouper(key='date', freq='D'))['sales']
        .sum()
        .reset_index()
    )
    line_source.data = dict(date=line_agg['date'], sales=line_agg['sales'])

    # ---- Bar chart -------------------------------------------------
    bar_agg = (
        filtered.groupby('category')['profit']
        .mean()
        .reset_index()
    )
    bar_source.data = dict(category=bar_agg['category'], profit=bar_agg['profit'])
    bar_fig.x_range.factors = list(bar_agg['category'])

# Link controls
region_ctrl.on_change('value', lambda attr, old, new: update_all())
cat_ctrl.on_change('value', lambda attr, old, new: update_all())
sales_ctrl.on_change('value_throttled', lambda attr, old, new: update_all())

# Initial fill
update_all()

# ------------------------------------------------------------------
# 7. Layout
# ------------------------------------------------------------------
controls = column(region_ctrl, cat_ctrl, sales_ctrl, width=260, sizing_mode="fixed")

tabs = Tabs(tabs=[
    TabPanel(child=scatter,      title="Scatter"),
    TabPanel(child=bar_fig,      title="Bar Chart"),
    TabPanel(child=data_table,   title="Table")
], sizing_mode="stretch_both")

main_row = row(controls, column(tabs, line_fig, sizing_mode="stretch_both"), sizing_mode="stretch_both")

curdoc().add_root(main_row)
curdoc().title = "Bokeh Interactive Sales Dashboard"