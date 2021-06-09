import dash_core_components as dcc
from dash_core_components.Dropdown import Dropdown
import dash_table
import dash_html_components as html
import dash_bootstrap_components as dbc
import flask

from .dash_url_helper import create_component_kwargs, State

from .core.config import *


#####################
# title must be set #
#####################

# The title gives the title of the app in the browser tab
title = "Cell Type Viewer"

###################################################################
# page_layout must be defined to take a state and return a layout #
###################################################################


def page_layout(state: State = {}):
    """This function returns the layout object for the dash app.
    The state parameter allows for URL-encoded parameter values.

    Parameters
    ----------
    state : State, optional
        URL state, a series of dicts that can provide parameter values, by default None

    Returns
    -------
    layout : list
        List of layout components for the dash app.
    """

    cell_type_query = html.Div(
        children=[
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div("Cell Type Table:"),
                            dcc.Dropdown(
                                **create_component_kwargs(
                                    state,
                                    id_inner="cell-type-table-menu",
                                    placeholder="Select a Cell Type Table",
                                    options=[],
                                    value=None,
                                ),
                                # options=[],
                                # id="cell-type-table-menu",
                                # placeholder="Select a Cell Type Table",
                            ),
                        ],
                        width={"size": 4, "offset": 1},
                        align="end",
                    ),
                    dbc.Col(
                        dbc.Button(
                            children="Submit",
                            id="submit-button",
                            color="primary",
                        ),
                        width={"size": 1, "offset": 2},
                        align="end",
                    ),
                    dbc.Col(
                        dcc.Loading(
                            id="main-loading",
                            children=html.Div(
                                id="main-loading-placeholder", children=""
                            ),
                            type="default",
                            style={"transform": "scale(0.8)"},
                        ),
                        width={"size": 1, "offset": 0},
                        align="end",
                    ),
                ],
                justify="start",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Div("Cell ID:"),
                            dcc.Input(
                                **create_component_kwargs(
                                    state,
                                    id_inner="anno-id",
                                    value="",
                                    type="text",
                                ),
                            ),
                        ],
                        width={"size": 1, "offset": 1},
                        align="end",
                    ),
                    dbc.Col(
                        [
                            dcc.Dropdown(
                                **create_component_kwargs(
                                    state,
                                    id_inner="id-type",
                                    options=[
                                        {
                                            "label": "Root ID",
                                            "value": "root_id",
                                        },
                                        {
                                            "label": "Nucleus ID",
                                            "value": "nucleus_id",
                                        },
                                        {
                                            "label": "Annotation ID",
                                            "value": "anno_id",
                                        },
                                    ],
                                    value="root_id",
                                )
                            )
                        ],
                        width={"size": 1},
                        align="end",
                    ),
                    # dbc.Col(
                    #     [
                    #         html.Div("Annotation ID:"),
                    #         dcc.Input(
                    #             **create_component_kwargs(
                    #                 state,
                    #                 id_inner="anno-id",
                    #                 value="",
                    #                 type="text",
                    #             ),
                    #         ),
                    #     ],
                    #     width={"size": 2, "offset": 1},
                    #     align="end",
                    # ),
                    # dbc.Col(
                    #     [
                    #         html.Div("Root ID:"),
                    #         dcc.Input(
                    #             **create_component_kwargs(
                    #                 state,
                    #                 value="",
                    #                 id_inner="root-id",
                    #                 type="text",
                    #             ),
                    #         ),
                    #     ],
                    #     width={"size": 2, "offset": 0},
                    #     align="end",
                    # ),
                    dbc.Col(
                        [
                            html.Div("Cell Type:"),
                            dcc.Input(
                                **create_component_kwargs(
                                    state,
                                    value="",
                                    id_inner="cell-type",
                                    type="text",
                                ),
                            ),
                        ],
                        width={"size": 1, "offset": 1},
                    ),
                    dbc.Col(
                        [html.Div(children="", id="report-text")],
                        width={"size": 2, "offset": 3},
                    ),
                ],
                justify="start",
                # no_gutters=True,
            ),
            html.Hr(),
        ]
    )
    data_table = html.Div(
        dbc.Row(
            [
                dbc.Col(
                    dash_table.DataTable(
                        id="data-table",
                        columns=[{"name": i, "id": i} for i in ct_table_columns],
                        data=[],
                        css=[
                            {
                                "selector": "table",
                                "rule": "table-layout: auto",
                            }
                        ],
                        style_cell={
                            "height": "auto",
                            "width": "12%",
                            "minWidth": "10%",
                            "maxWidth": "15%",
                            "whiteSpace": "normal",
                            "font-size": "11px",
                        },
                        style_header={"font-size": "12px", "fontWeight": "bold"},
                        sort_action="native",
                        sort_mode="multi",
                        filter_action="native",
                        row_selectable="multi",
                        page_current=0,
                        page_action="native",
                        page_size=50,
                    ),
                    width={"size": 10, "offset": 1},
                )
            ],
            justify="start",
        )
    )

    ngl_link = dbc.Row(
        [
            dbc.Col(
                dcc.Loading(
                    id="loading-link",
                    children=html.Div(id="link-loading-placeholder", children=""),
                    type="dot",
                    style={"transform": "scale(0.75)"},
                ),
                width={"size": 1, "offset": 0},
                align="circle",
            ),
            dbc.Col(
                html.A(
                    "Neuroglancer Link",
                    id="ngl-link",
                    href="",
                    target="_blank",
                    style={"font-size": "18px"},
                ),
                width={"size": 2, "offset": 0},
                align="start",
            ),
            dbc.Col(
                dbc.Button(
                    id="reset-selection",
                    children="Reset Selection",
                    color="primary",
                    size="sm",
                ),
                width={"size": 1, "offset": 0},
            ),
        ],
        justify="start",
    )

    datastack_comp = (
        dcc.Input(
            **create_component_kwargs(
                state,
                id_inner="datastack",
                value=DEFAULT_DATASTACK,
                type="text",
            ),
        ),
    )

    layout = html.Div(
        children=[
            html.Div("Table Lookup"),
            html.Div(cell_type_query),
            html.Div(ngl_link),
            html.Div(data_table),
            html.Div(datastack_comp, style={"display": "none"}),
            dcc.Store(id="client-info-json"),
        ]
    )
    return layout


######################################################
# Leave this rest alone for making the template work #
######################################################

url_bar_and_content_div = html.Div(
    [dcc.Location(id="url", refresh=False), html.Div(id="page-layout")]
)


def app_layout():
    # https://dash.plotly.com/urls "Dynamically Create a Layout for Multi-Page App Validation"
    if flask.has_request_context():  # for real
        return url_bar_and_content_div
    # validation only
    return html.Div([url_bar_and_content_div, *page_layout()])
