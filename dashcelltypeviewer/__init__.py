from dash import Dash
from .callbacks import register_callbacks
from .layout import title, page_layout, app_layout
from .dash_url_helper import setup
from .external_stylesheets import external_stylesheets
import flask

__version__ = "0.0.1"

#######################################
# This function should not be changed #
#######################################


def create_app(name=__name__, config={}, **kwargs):
    if "external_stylesheets" not in kwargs:
        kwargs["external_stylesheets"] = external_stylesheets
    app = Dash(name, **kwargs)
    app.title = title
    app.layout = app_layout
    setup(app, page_layout=page_layout)
    register_callbacks(app, config)
    return app
