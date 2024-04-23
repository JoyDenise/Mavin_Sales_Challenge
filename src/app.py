from dash import Dash, dcc, html
import pandas as pd
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash_bootstrap_templates import load_figure_template

from dash.dependencies import Input, Output

import plotly.express as px

dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"

sales = pd.read_pickle("sales_pipeline_and_teams.pkl")
sales_teams = pd.read_csv("sales_teams.csv")
products = pd.read_csv("products.csv")


app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE, dbc_css])
server = app.server

load_figure_template("SOLAR")

app.layout = dbc.Container(
    [
        dbc.Row([html.H1(id="header_tag", style={"textAlign": "center"})]),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                html.P("Choose Manager", style={"textAlign": "center"}),
                                dcc.Dropdown(
                                    id="manager_tag",
                                    options=list(sales_teams.manager.unique()),
                                    value="",
                                ),
                                html.Br(),
                                html.Hr(),
                                html.P(
                                    "Select Year to Review",
                                    style={"textAlign": "center"},
                                ),
                                dcc.Dropdown(
                                    id="year_tag",
                                    options=list(
                                        sales.close_fiscal_year.value_counts()
                                        .sort_index()
                                        .index
                                    )[1:],
                                    value="2017",
                                ),
                                html.Br(),
                                html.Hr(),
                                html.P("Select Quarter", style={"textAlign": "center"}),
                                dcc.RadioItems(
                                    id="quarter_tag",
                                    options=list(sales.quarter_tags.unique())[:4],
                                    value="Q1",
                                ),
                                html.Hr(),
                                html.P(
                                    "Only for the Bar Plots",
                                    style={"textAlign": "center"},
                                ),
                                dcc.RadioItems(
                                    id="top_bottom",
                                    options=["top to bottom", "bottom to top"],
                                    value="top to bottom",
                                ),
                            ]
                        )
                    ],
                    width=2,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H3(
                                            "Revenue Generated in Quarter",
                                            style={"textAlign": "center"},
                                        )
                                    ],
                                    className="text-title",
                                ),
                                dcc.Graph(id="pie_revenue"),
                            ]
                        )
                    ],
                    width=5,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H3(
                                            "Top Sold Product by Units",
                                            style={"textAlign": "center"},
                                        ),
                                        html.Br(),
                                        html.H5(
                                            id="product_tag",
                                            style={"textAlign": "center"},
                                        ),
                                        html.H5(
                                            id="product_price",
                                            style={"textAlign": "center"},
                                        ),
                                        html.Br(),
                                        html.Hr(),
                                        html.H3(
                                            "Top Revenue Generating Product",
                                            style={"textAlign": "center"},
                                        ),
                                        html.Br(),
                                        html.H5(
                                            id="top_revenue_product",
                                            style={"textAlign": "center"},
                                        ),
                                        html.H5(
                                            id="product_revenue",
                                            style={"textAlign": "center"},
                                        ),
                                        html.Br(),
                                        html.Hr(),
                                        html.H3(
                                            "Top Revenue Generating Client",
                                            style={"textAlign": "center"},
                                        ),
                                        html.Br(),
                                        html.H5(
                                            id="top_client",
                                            style={"textAlign": "center"},
                                        ),
                                        html.Br(),
                                    ]
                                )
                            ]
                        )
                    ],
                    width=5,
                ),
            ]
        ),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H3(
                                            "Quarter on Quarter Revenue",
                                            style={"textAlign": "center"},
                                        )
                                    ]
                                ),
                                dcc.Graph(id="quarter_revenue_line"),
                            ]
                        )
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H3(
                                            "Closers who 'Won' Deals",
                                            style={"textAlign": "center"},
                                        )
                                    ]
                                ),
                                dcc.Graph(id="top_closes_bar"),
                            ]
                        )
                    ],
                    width=4,
                ),
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H3(
                                            "Revenue Generated by Agent",
                                            style={"textAlign": "center"},
                                        )
                                    ]
                                ),
                                dcc.Graph(id="top_revenue_bar"),
                            ]
                        )
                    ],
                    width=4,
                ),
            ]
        ),
    ]
)


@app.callback(
    Output("pie_revenue", "figure"),
    Input("manager_tag", "value"),
    Input("year_tag", "value"),
    Input("quarter_tag", "value"),
)
def donut_chart(manager, close_year, close_quarter):
    if not manager:
        raise PreventUpdate
    if not close_year:
        raise PreventUpdate

    closing_year = int(pd.to_numeric(close_year))

    manager_df = (
        sales.query("manager == @manager")
        .query("close_fiscal_year == @closing_year")
        .query("quarter_tags == @close_quarter")
        .reset_index(drop=True)
    )
    manager_name = manager_df.loc[0, "manager"]
    manager_revenue = manager_df.close_value.sum()
    other_managers_revenue = (
        sales.query("close_fiscal_year == @closing_year")
        .query("quarter_tags == @close_quarter")
        .close_value.sum()
        - manager_revenue
    )

    fig = px.pie(
        values=[manager_revenue, other_managers_revenue],
        names=[manager_name, "Other Managers"],
        hole=0.6,
    )

    return fig


@app.callback(
    Output("header_tag", "children"),
    Output("product_tag", "children"),
    Output("product_price", "children"),
    Output("top_revenue_product", "children"),
    Output("product_revenue", "children"),
    Output("top_client", "children"),
    Input("manager_tag", "value"),
    Input("year_tag", "value"),
    Input("quarter_tag", "value"),
)
def texts_update(manager, year_close, close_quarter):
    if not manager:
        raise PreventUpdate
    if not year_close:
        raise PreventUpdate

    header_title = f"Sales Data Analysis by Manager {manager}"

    closing_year = int(pd.to_numeric(year_close))
    df = (
        sales.query("manager == @manager")
        .query("close_fiscal_year == @closing_year")
        .query("quarter_tags == @close_quarter")
        .query("deal_stage == 'Won'")
    )

    top_product = (
        df.groupby("product")
        .agg({"opportunity_id": "count"})
        .sort_values(by="opportunity_id", ascending=False)
        .reset_index()
        .loc[0, "product"]
    )
    product_price = f'Unit price of USD$ {products.groupby("product").agg({"sales_price": "sum"}).loc[top_product, "sales_price"]:,.0f}'
    top_revenue_product = (
        df.groupby("product")
        .agg({"close_value": "sum"})
        .sort_values(by="close_value", ascending=False)
        .reset_index()
        .loc[0, "product"]
    )
    product_revenue = f'USD$ {df.groupby("product").agg({"close_value": "sum"}).sort_values(by="close_value", ascending=False).reset_index().loc[0,"close_value"]:,.0f}'
    top_client = (
        df.groupby("account")
        .agg({"close_value": "sum"})
        .sort_values(by="close_value", ascending=False)
        .reset_index()
        .loc[0, "account"]
    )

    return (
        header_title,
        top_product,
        product_price,
        top_revenue_product,
        product_revenue,
        top_client,
    )


@app.callback(
    Output("top_closes_bar", "figure"),
    Output("top_revenue_bar", "figure"),
    Input("manager_tag", "value"),
    Input("year_tag", "value"),
    Input("quarter_tag", "value"),
    Input("top_bottom", "value"),
)
def bar_plots_update(manager, year_close, close_quarter, groupings):
    if not manager:
        raise PreventUpdate
    if not year_close:
        raise PreventUpdate

    closing_year = int(pd.to_numeric(year_close))

    df = (
        sales.query("manager == @manager")
        .query("close_fiscal_year == @closing_year")
        .query("quarter_tags == @close_quarter")
        .query("deal_stage == 'Won'")
    )

    top_closers = (
        df.groupby("sales_agent")
        .agg({"account": "count"})
        .sort_values(by="account", ascending=False)
        .reset_index()
    )

    bottom_closers = (
        df.groupby("sales_agent")
        .agg({"account": "count"})
        .sort_values(by="account")
        .reset_index()
    )

    top_revenue_gen = (
        df.groupby("sales_agent")
        .agg({"close_value": "sum"})
        .sort_values(by="close_value", ascending=False)
        .reset_index()
    )

    bottom_revenue_gen = (
        df.groupby("sales_agent")
        .agg({"close_value": "sum"})
        .sort_values(by="close_value")
        .reset_index()
    )

    if groupings == "top to bottom":
        fig = px.bar(
            top_closers,
            x="sales_agent",
            y="account",
            labels={"account": "Frequency", "sales_agent": "Sales Agent"},
        ).update_layout(showlegend=False)

        fig1 = px.bar(
            top_revenue_gen,
            x="sales_agent",
            y="close_value",
            labels={"close_value": "Revenue", "sales_agent": "Sales Agent"},
        ).update_layout(showlegend=False)
    else:
        fig = px.bar(
            bottom_closers,
            x="sales_agent",
            y="account",
            labels={"account": "Frequency", "sales_agent": "Sales Agent"},
        ).update_layout(showlegend=False)

        fig1 = px.bar(
            bottom_revenue_gen,
            x="sales_agent",
            y="close_value",
            labels={"close_value": "Revenue", "sales_agent": "Sales Agent"},
        ).update_layout(showlegend=False)

    return fig, fig1


@app.callback(
    Output("quarter_revenue_line", "figure"),
    Input("manager_tag", "value"),
)
def qoq_revenue_update(manager):
    if not manager:
        raise PreventUpdate

    df = sales.query("manager == @manager")

    fig = px.line(
        df.groupby("close_quarter_tags")
        .agg({"close_value": "sum"})
        .sort_index()
        .reset_index(),
        x="close_quarter_tags",
        y="close_value",
        labels={"close_value": "Revenue", "close_quarter_tags": "Quarter"},
    ).update_layout(showlegend=False)

    return fig


if __name__ == "__main__":
    app.run_server(jupyter_mode="tab")
