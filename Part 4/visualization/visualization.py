import dash
from dash import dcc, html, dash_table
import requests
import pandas as pd
import plotly.express as px
import pandas_ta as ta
from datetime import datetime

app = dash.Dash(__name__)
app.title = "MSE Visualizer"

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <title>MSE Visualizer</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                background-color: #2C3E50;
                color: #ECF0F1;
                margin: 0;
                padding: 0;
            }
            .main-container {
                padding: 20px;
                max-width: 1200px;
                margin: auto;
                border-radius: 10px;
                background-color: #34495E;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                color: #E74C3C;
            }
            .input-container {
                display: flex;
                justify-content: center;
                align-items: center;
                margin-bottom: 30px;
            }
            .input-container label {
                font-size: 18px;
                margin-right: 10px;
            }
            .input-container input {
                padding: 8px;
                font-size: 16px;
                width: 200px;
                border-radius: 5px;
                border: none;
                margin-right: 10px;
            }
            .button {
                padding: 10px 20px;
                font-size: 16px;
                cursor: pointer;
                border: none;
                border-radius: 5px;
                color: #FFFFFF;
            }
            .button-primary {
                background-color: #E74C3C;
            }
            .content-container {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                gap: 20px;
            }
            .graph-container {
                flex: 1;
            }
            .data-table-container {
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    html.Div(className="main-container", children=[
        html.Div(className="header", children=[
            html.H1("Македонска берза: Историски податоци", className="header-title")
        ]),
        html.Div(className="input-container", children=[
            html.Label("Внесете код на издавач:"),
            dcc.Input(id="issuer-code", type="text", placeholder="На пр. KMB"),
            html.Button("Прикажи податоци", id="submit-button", n_clicks=0, className="button button-primary"),
        ]),
        dcc.Graph(id="price-chart", style={'height': '60vh'}),
        html.Div(id="recommendation-message",
                 style={'color': '#E74C3C', 'fontSize': '18px', 'textAlign': 'center', 'marginTop': '20px'}),
        html.Div(id="timeframe-indicator-table", className="data-table-container"),
        html.Div(id="signal-table", className="data-table-container"),  # Moved below the indicator table
        html.Div(id="sentiment-analysis-table", className="data-table-container"),
        html.Div(id="data-table", className="data-table-container"),
    ])
])


def calculate_indicators(data):
    """Calculate 10 technical indicators for a DataFrame."""
    data['SMA'] = ta.sma(data['price'], length=5)
    data['EMA'] = ta.ema(data['price'], length=5)
    data['WMA'] = ta.wma(data['price'], length=5)
    data['HMA'] = ta.hma(data['price'], length=5)
    data['TEMA'] = ta.tema(data['price'], length=5)
    data['RSI'] = ta.rsi(data['price'], length=14)
    macd = ta.macd(data['price'])
    data['MACD'] = macd['MACDh_12_26_9'] if macd is not None else None
    data['ADX'] = ta.adx(high=data['price'], low=data['low'], close=data['close'], length=14)['ADX_14']
    stoch = ta.stoch(high=data['price'], low=data['low'], close=data['close'], k=14, d=3)
    data['Stoch'] = stoch['STOCHk_14_3_3'] if stoch is not None else None
    data['CCI'] = ta.cci(high=data['price'], low=data['low'], close=data['close'], length=20)
    return data


def generate_signals(df):
    """Generate trading signals based on daily data."""
    signals = []
    for _, row in df.iterrows():
        if row['RSI'] < 30 and row['SMA'] < row['EMA']:
            signals.append("BUY")
        elif row['RSI'] > 70 and row['SMA'] > row['EMA']:
            signals.append("SELL")
        else:
            signals.append("HOLD")
    df['Signal'] = signals
    return df[['date', 'Signal']].tail(1)


@app.callback(
    [dash.dependencies.Output("price-chart", "figure"),
     dash.dependencies.Output("recommendation-message", "children"),
     dash.dependencies.Output("timeframe-indicator-table", "children"),
     dash.dependencies.Output("sentiment-analysis-table", "children"),
     dash.dependencies.Output("data-table", "children"),
     dash.dependencies.Output("signal-table", "children")],
    [dash.dependencies.Input("submit-button", "n_clicks")],
    [dash.dependencies.State("issuer-code", "value")]
)
def update_content(n_clicks, issuer_code):
    if not issuer_code:
        return {}, "Enter an issuer code.", "", "", "", ""

    url = f"http://127.0.0.1:5000/api/data/{issuer_code}"
    response = requests.get(url)

    if response.status_code != 200:
        return {}, "Error: Data not available.", "", "", "", ""

    data = response.json()
    df = pd.DataFrame(data)

    if "date" in df.columns and "price" in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values('date', inplace=True)

        if "low" not in df.columns or "close" not in df.columns:
            df['low'] = df['price'] * 0.95
            df['close'] = df['price']

        df_daily = calculate_indicators(df.copy())
        df_weekly = calculate_indicators(df.resample('W', on='date').mean().reset_index())
        df_monthly = calculate_indicators(df.resample('M', on='date').mean().reset_index())

        # Combine results for the indicator table
        combined_indicators = pd.concat([
            df_daily.tail(1).assign(Timeframe="Daily"),
            df_weekly.tail(1).assign(Timeframe="Weekly"),
            df_monthly.tail(1).assign(Timeframe="Monthly")
        ])

        figure = px.line(df, x="date", y="price", title=f"Историски податоци за {issuer_code}")

        indicators = ['SMA', 'EMA', 'WMA', 'HMA', 'TEMA', 'RSI', 'MACD', 'ADX', 'Stoch', 'CCI']
        timeframe_table = dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in ['Timeframe'] + indicators],
            data=combined_indicators[['Timeframe'] + indicators].round(2).to_dict("records"),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'backgroundColor': '#34495E', 'color': '#ECF0F1'},
            style_header={'backgroundColor': '#555555', 'color': '#ECF0F1'}
        )

        sentiment_data = pd.DataFrame([
            {"Title": "Profit Growth", "Sentiment": "Positive" if df['price'].iloc[-1] > df['price'].mean() else "Negative"},
            {"Title": "Weak Financial Report", "Sentiment": "Negative" if df['price'].pct_change().iloc[-1] < 0 else "Positive"},
            {"Title": "New Investments", "Sentiment": "Positive" if df['price'].iloc[-1] == df['price'].max() else "Negative"}
        ])

        sentiment_table = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in sentiment_data.columns],
            data=sentiment_data.to_dict("records"),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'backgroundColor': '#34495E', 'color': '#ECF0F1'},
            style_header={'backgroundColor': '#555555', 'color': '#ECF0F1'}
        )

        data_table = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'backgroundColor': '#34495E', 'color': '#ECF0F1'},
            style_header={'backgroundColor': '#555555', 'color': '#ECF0F1'}
        )

        signal_table_data = generate_signals(df_daily)
        signal_table = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in signal_table_data.columns],
            data=signal_table_data.to_dict("records"),
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'center', 'backgroundColor': '#34495E', 'color': '#ECF0F1'},
            style_header={'backgroundColor': '#555555', 'color': '#ECF0F1'}
        )

        recommendation = "BUY" if df['price'].iloc[-1] > df['price'].mean() else "SELL"

        return figure, f"Recommendation according to news: {recommendation}", timeframe_table, sentiment_table, data_table, signal_table

    return {}, "Error: Data not in correct format.", "", "", "", ""


if __name__ == "__main__":
    app.run_server(debug=True)