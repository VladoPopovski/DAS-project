import dash
from dash import dcc, html, dash_table
import requests
import pandas as pd
import plotly.express as px


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
            .image-container {
                flex: 1;
                text-align: center;
            }
            .image-container img {
                max-width: 100%;
                height: auto;
                border-radius: 10px;
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
            html.Img(src="/assets/market-research.png", alt="Logo"),
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
            html.Div(className="image-container", children=[
                html.Img(src="/assets/—Pngtree—businessman walking on growing graph_5368609.png", alt="Graph Illustration")
            ]),
            html.Div(className="graph-container", children=[
                dcc.Graph(id="price-chart", style={'height': '60vh'}),
            ]),
        ]),
        html.Div(id="data-table", className="data-table-container"),
    ])
])

@app.callback(
    [dash.dependencies.Output("price-chart", "figure"),
     dash.dependencies.Output("data-table", "children"),
     dash.dependencies.Output("issuer-code", "value")],
    [dash.dependencies.Input("submit-button", "n_clicks"),
     dash.dependencies.Input("reset-button", "n_clicks")],
    [dash.dependencies.State("issuer-code", "value")]
)
def update_content(submit_clicks, reset_clicks, issuer_code):
    ctx = dash.callback_context
    if not ctx.triggered:
        return px.line(title="Внесете код на издавач за приказ"), html.Div("Внесете код на издавач за приказ."), ""

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == "reset-button":
        return px.line(title="Графикон"), html.Div(), ""

    if not issuer_code:
        return px.line(title="Внесете код на издавач за приказ"), html.Div("Внесете код на издавач за приказ."), issuer_code


    url = f"http://127.0.0.1:5000/api/data/{issuer_code}"
    response = requests.get(url)

    if response.status_code != 200:
        return px.line(title="Грешка: Податоците не се достапни"), html.Div("Грешка: Податоците не се достапни."), issuer_code


    data = response.json()
    df = pd.DataFrame(data)

    # Ensure required columns exist
    if "date" in df.columns and "price" in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values('date', inplace=True)


        fig = px.line(
            df, x="date", y="price", title=f"Историски податоци за {issuer_code}",
            color_discrete_sequence=["#E74C3C", "#3498DB"]
        )


        table = dash_table.DataTable(
            id='data-table',
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict('records'),
            style_table={'overflowX': 'auto', 'backgroundColor': '#34495E'},
            style_cell={
                'textAlign': 'center', 'color': '#ECF0F1', 'backgroundColor': '#34495E',
                'padding': '10px', 'fontSize': '14px', 'border': '1px solid #555555'
            },
            style_header={'backgroundColor': '#555555', 'fontWeight': 'bold', 'color': '#ECF0F1'},
            page_size=10,
        )

        return fig, table, issuer_code
    else:
        return px.line(title="Грешка: Податоците не се во соодветен формат"), html.Div("Грешка: Податоците не се во соодветен формат."), issuer_code


def run_dash_server():
    """Run the Dash server"""
    app.run_server(debug=True, port=8050)


if __name__ == "__main__":
    run_dash_server()
