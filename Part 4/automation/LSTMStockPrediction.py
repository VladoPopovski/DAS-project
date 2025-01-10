import dash
from dash import dcc, html, dash_table
import requests
import pandas as pd
import plotly.express as px
import pandas_ta as ta
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, Dense

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
                position: relative;
            }
            .header img {
                position: absolute;
                top: 0;
                left: 20px;
                width: 60px;
                height: 60px;
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
            .button-secondary {
                background-color: #95A5A6;
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
            html.Img(src="../visualization/assets/market-research.png", alt="Logo"),
            html.H1("Македонска берза: Историски податоци", className="header-title")
        ]),
        html.Div(className="input-container", children=[
            html.Label("Внесете код на издавач:", style={'fontSize': '18px'}),
            dcc.Input(id="issuer-code", type="text", placeholder="На пр. KMB", style={'marginRight': '10px'}),
            html.Button("Прикажи податоци", id="submit-button", n_clicks=0,
                        className="button button-primary", style={'marginRight': '10px'}),
            html.Button("Ресетирај податоци", id="reset-button", n_clicks=0,
                        className="button button-secondary"),
        ]),
        html.Div(className="content-container", children=[
            html.Div(className="graph-container", children=[
                dcc.Graph(id="price-chart", style={'height': '60vh'}),
                dcc.Graph(id="prediction-chart", style={'height': '60vh'}),
            ]),
            html.Div(id="indicator-table", className="data-table-container"),
        ]),
        html.Div(id="data-table", className="data-table-container"),
    ])
])


def calculate_indicators(data):
    """Calculate technical indicators for a DataFrame."""
    data['SMA'] = ta.sma(data['price'], length=5)
    data['EMA'] = ta.ema(data['price'], length=5)
    data['WMA'] = ta.wma(data['price'], length=5)
    data['HMA'] = ta.hma(data['price'], length=5)
    data['VWMA'] = ta.vwma(data['price'], data['Volume'], length=5)
    data['RSI'] = ta.rsi(data['price'], length=14)
    data['MACD'] = ta.macd(data['price'])['MACD_12_26_9']
    data['Stochastic'] = ta.stoch(data['Max'], data['Min'], data['price'])['STOCHk_14_3_3']
    data['CCI'] = ta.cci(data['Max'], data['Min'], data['price'], length=14)
    data['Williams %R'] = ta.willr(data['Max'], data['Min'], data['price'], length=14)
    return data


def prepare_data(data):
    # Prepare data for LSTM
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data[['price']].values)

    train_size = int(len(scaled_data) * 0.7)
    train_data = scaled_data[:train_size]
    test_data = scaled_data[train_size:]

    X_train, y_train = [], []
    X_test, y_test = []

    for i in range(60, len(train_data)):
        X_train.append(train_data[i - 60:i, 0])
        y_train.append(train_data[i, 0])

    for i in range(60, len(test_data)):
        X_test.append(test_data[i - 60:i, 0])
        y_test.append(test_data[i, 0])

    X_train, y_train = np.array(X_train), np.array(y_train)
    X_test, y_test = np.array(X_test), np.array(y_test)

    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    return X_train, y_train, X_test, y_test, scaler


def build_model():
    # Build LSTM model
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(60, 1)))
    model.add(LSTM(units=50))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


@app.callback(
    [dash.dependencies.Output("price-chart", "figure"),
     dash.dependencies.Output("prediction-chart", "figure"),
     dash.dependencies.Output("indicator-table", "children"),
     dash.dependencies.Output("data-table", "children"),
     dash.dependencies.Output("issuer-code", "value")],
    [dash.dependencies.Input("submit-button", "n_clicks"),
     dash.dependencies.Input("reset-button", "n_clicks")],
    [dash.dependencies.State("issuer-code", "value")]
)
def update_content(submit_clicks, reset_clicks, issuer_code):
    ctx = dash.callback_context
    if not ctx.triggered:
        return (
            px.line(title="Внесете код на издавач за приказ"),
            px.line(title="Предвидување на цени на акции"),
            html.Div("Внесете код на издавач за приказ."),
            html.Div("Внесете код на издавач за приказ."),
            ""
        )

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "reset-button":
        return (
            px.line(title="Графикон"),
            px.line(title="Предвидување на цени на акции"),
            html.Div(),
            html.Div(),
            ""
        )

    if not issuer_code:
        return (
            px.line(title="Внесете код на издавач за приказ"),
            px.line(title="Предвидување на цени на акции"),
            html.Div("Внесете код на издавач за приказ."),
            html.Div("Внесете код на издавач за приказ."),
            ""
        )

    url = f"http://127.0.0.1:5000/api/data/{issuer_code}"
    response = requests.get(url)

    if response.status_code != 200:
        return (
            px.line(title="Грешка: Податоците не се достапни"),
            px.line(title="Грешка: Податоците не се достапни"),
            html.Div("Грешка: Податоците не се достапни."),
            issuer_code
        )

    data = response.json()
    df = pd.DataFrame(data)

    # Ensure required columns exist
    if "date" in df.columns and "price" in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values('date', inplace=True)

        # Calculate technical indicators
        df = calculate_indicators(df)

        # Prepare data for LSTM
        X_train, y_train, X_test, y_test, scaler = prepare_data(df)

        # Build and train LSTM model
        model = build_model()
        model.fit(X_train, y_train, epochs=10, batch_size=32)

        # Make predictions
        predictions = model.predict(X_test)
        predictions = scaler.inverse_transform(predictions)

        # Add predictions to dataframe
        df['predicted_price'] = np.nan
        df.iloc[len(df) - len(predictions):, df.columns.get_loc('predicted_price')] = predictions.flatten()

        # Price chart
        price_fig = px.line(df, x="date", y="price", title=f"Историски податоци за {issuer_code}")

        # Prediction chart
        prediction_fig = px.line(df, x="date", y=["price", "predicted_price"],
                                 title=f"Предвидување на цени за {issuer_code}")

        # Indicators table
        indicator_df = pd.DataFrame({
            "Indicator": ["SMA", "EMA", "WMA", "HMA", "VWMA", "RSI", "MACD", "Stochastic", "CCI", "Williams %R"],
            "Value": [
                df['SMA'].iloc[-1],
                df['EMA'].iloc[-1],
                df['WMA'].iloc[-1],
                df['HMA'].iloc[-1],
                df['VWMA'].iloc[-1],
                df['RSI'].iloc[-1],
                df['MACD'].iloc[-1],
                df['Stochastic'].iloc[-1],
                df['CCI'].iloc[-1],
                df['Williams %R'].iloc[-1]
            ]
        }).round(2)
        indicator_table = dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in indicator_df.columns],
            data=indicator_df.to_dict('records'),
            style_table={'overflowX': 'auto', 'backgroundColor': '#34495E'},
            style_cell={'textAlign': 'center', 'color': '#ECF0F1', 'backgroundColor': '#34495E'},
            style_header={'backgroundColor': '#555555', 'color': '#ECF0F1'}
        )

        # Data table
        data_table = dash_table.DataTable(
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict('records'),
            style_table={'overflowX': 'auto', 'backgroundColor': '#34495E'},
            style_cell={'textAlign': 'center', 'color': '#ECF0F1', 'backgroundColor': '#34495E'},
            style_header={'backgroundColor': '#555555', 'color': '#ECF0F1'}
        )

        return price_fig, prediction_fig, indicator_table, data_table, ""
    else:
        return (
            px.line(title="Грешка: Податоците не се во соодветен формат"),
            px.line(title="Грешка: Податоците не се во соодветен формат"),
            html.Div("Грешка: Податоците не се во соодветен формат."),
            issuer_code
        )


if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
