import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from sklearn import datasets
from sklearn.cluster import KMeans

df = pd.read_csv("Output_file1.csv")

val = df[df["Publication number"] == df["Publication number"][0]]
values = val[["Computer_technology", 'Telecommunication', 'Mechanical']].values[0]
data = [go.Bar(x=['Computer_technology', 'Telecommunication', 'Mechanical'],
               y=values,
               textposition="outside",
               marker=dict(color=["green", "blue", "red"]))]
layout = go.Layout(title="Percent of Entities in Description",
                   hovermode="x",
                   plot_bgcolor="white")
fig = go.Figure(data=data, layout=layout)

dropdown_variables = ['Mechanical', 'Telecommunication',
                      'Computer_technology']

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

text_input = dbc.Card(
    [html.Div([
        html.Label("Publication No:")]),
        dbc.Input(
            id="input",
            placeholder="Enter Publication No",
            type="text",
            value=df["Publication number"][0],
            className="mb-3",
            style={"color": "black", "border": "3px solid lightblue"}
        )

    ], style={"color": "black", "border": "3px solid lightblue"})

graph = html.Div([
    dcc.Graph(
        id='Barplot',
        figure=fig,
    )
], style={"border": "3px solid lightblue"})

app.layout = dbc.Container([
    html.H1("Patent Technologies Search"),
    html.Hr(),
    dbc.Row([
        dbc.Col(text_input, md=4, className="mr-1"),
        dbc.Col(graph, md=8)],
    )
],
    className="mb-5")


@app.callback(Output("Barplot", "figure"),
              [Input("input", "value")]
              )
def update_fig(number):
    val = df[df["Publication number"] == number]
    values = val[['Computer_technology', 'Telecommunication', 'Mechanical']].values[0]
    data = [go.Bar(x=['Computer_technology', "Audio_video", 'Telecommunication', 'Mechanical'],
                   y=values,
                   textposition="outside",
                   marker={'color': ["green", "blue", "red"]})]
    layout = go.Layout(title="Percent of Entities in Description", hovermode="x", plot_bgcolor="white")
    fig = go.Figure(data=data, layout=layout)

    return fig


app.run_server()
if __name__ == "__main__":
    app.run_server(debug=True)
