from dash.dependencies import Input, Output, State
from annotationframeworkclient.frameworkclient import FrameworkClient
from .core.dataframe_utilities import *
from .core.link_utilities import *
from .core.config import *
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import flask
import datetime

# Callbacks using data from URL-encoded parameters requires this import
from .dash_url_helper import _COMPONENT_ID_TYPE

EMPTY_INFO_CACHE = {"aligned_volumes": {}}

InputDatastack = Input({"id_inner": "datastack", "type": _COMPONENT_ID_TYPE}, "value")
OutputCellTypeMenuOptions = Output(
    {"id_inner": "cell-type-table-menu", "type": _COMPONENT_ID_TYPE}, "options"
)
StateCellTypeMenu = State(
    {"id_inner": "cell-type-table-menu", "type": _COMPONENT_ID_TYPE}, "value"
)
StateCellType = State({"id_inner": "cell-type", "type": _COMPONENT_ID_TYPE}, "value")
# StateRootID = State({"id_inner": "root-id", "type": _COMPONENT_ID_TYPE}, "value")
StateAnnoID = State({"id_inner": "anno-id", "type": _COMPONENT_ID_TYPE}, "value")
StateCategoryID = State({"id_inner": "id-type", "type": _COMPONENT_ID_TYPE}, "value")


def make_client(datastack, config):
    auth_token = flask.g.get("auth_token", None)
    server_address = config.get("SERVER_ADDRESS", DEFAULT_SERVER_ADDRESS)
    client = FrameworkClient(
        datastack, server_address=server_address, auth_token=auth_token
    )
    return client


NUCLEUS_TABLE = "nucleus_neuron_svm"


def get_root_id_from_nuc_id(nuc_id, client, timestamp, nucleus_table=NUCLEUS_TABLE):
    df = client.materialize.live_query(
        nucleus_table, timestamp=timestamp, filter_equal_dict={"id": nuc_id}
    )
    if len(df) == 0:
        return None
    else:
        return df.iloc[0]["pt_root_id"]


######################################
# register_callbacks must be defined #
######################################


def register_callbacks(app, config):
    """This function must be present and add all callbacks to the app.
    Note that inputs from url-encoded values have a different structure than other values.
    A config dict is also allowed to configure standard parameter values for use in callback functions.

    Here, we show basic examples of using the three parameters defined in the layout.page_layout function.

    Parameters
    ----------
    app : Dash app
        Pre-made dash app
    config : dict
        Dict for standard parameter values
    """

    @app.callback(
        OutputCellTypeMenuOptions,
        InputDatastack,
    )
    def cell_type_dropdown(datastack):
        try:
            client = make_client(datastack, config)
        except:
            return []

        tables = client.materialize.get_tables()
        ct_tables = []
        for t in tables:
            meta = client.materialize.get_table_metadata(t)
            if meta["schema"] == "cell_type_local":
                ct_tables.append(t)
        return [{"label": t, "value": t} for t in ct_tables]

    @app.callback(
        Output("data-table", "data"),
        Output("report-text", "value"),
        Output("main-loading-placeholder", "value"),
        Output("client-info-json", "data"),
        Input("submit-button", "n_clicks"),
        InputDatastack,
        StateCellTypeMenu,
        StateAnnoID,
        StateCategoryID,
        StateCellType,
    )
    def update_table(clicks, datastack, cell_type_table, anno_id, id_type, cell_type):
        try:
            client = make_client(datastack, config)
            info_cache = client.info.info_cache[datastack]
            info_cache["global_server"] = client.server_address
        except Exception as e:
            return [], str(e), "", EMPTY_INFO_CACHE

        if cell_type_table is None:
            return [], "", "", info_cache

        if len(anno_id) == 0:
            anno_id = None
            id_type = "anno_id"

        timestamp = datetime.datetime.now()
        if anno_id is None:
            root_id = None
        else:
            if id_type == "root_id":
                root_id = int(anno_id)
                anno_id = None
            elif id_type == "nucleus_id":
                root_id = get_root_id_from_nuc_id(int(anno_id), client, timestamp)
                anno_id = None
            elif id_type == "anno_id":
                anno_id = int(anno_id)
                root_id = None
            else:
                raise ValueError('id_type must be either "root_id" or "nucleus_id"')

        if cell_type is None:
            cell_type == ""

        filter_equal_dict = {}
        if anno_id is not None and root_id is not None:
            df = pd.DataFrame(columns=ct_table_columns)
            output_report = "Please set either anno id or root id but not both"
        else:
            if anno_id is not None:
                filter_equal_dict.update({"id": anno_id})
            if root_id is not None:
                filter_equal_dict.update({"pt_root_id": root_id})
            if len(cell_type) > 0:
                filter_equal_dict.update({"cell_type": cell_type})
            if len(filter_equal_dict) == 0:
                filter_equal_dict = None

            try:
                df = client.materialize.live_query(
                    cell_type_table,
                    filter_equal_dict=filter_equal_dict,
                    timestamp=timestamp,
                    split_positions=True,
                )
                output_report = ""
            except Exception as e:
                df = pd.DataFrame(columns=ct_table_columns)
                output_report = str(e)

        ct_df = stringify_root_ids(process_dataframe(df))
        return (
            ct_df.to_dict("records"),
            output_report,
            "",
            info_cache,
        )

    @app.callback(
        Output("data-table", "selected_rows"),
        Input("reset-selection", "n_clicks"),
    )
    def reset_selection(n_clicks):
        return []

    @app.callback(
        Output("ngl-link", "href"),
        Output("link-loading-placeholder", "children"),
        Input("data-table", "derived_virtual_data"),
        Input("data-table", "derived_virtual_selected_rows"),
        Input("client-info-json", "data"),
    )
    def update_link(rows, selected_rows, info_cache):
        if rows is None or len(rows) == 0:
            sb = generate_statebuilder(info_cache, anno_layer="anno")
            return sb.render_state(None, return_as="url"), ""
        else:
            df = pd.DataFrame(rows)
            df["pt_position"] = df.apply(assemble_pt_position, axis=1)
            return generate_url_cell_types(selected_rows, df, info_cache), ""

    pass

    @app.callback(
        Output("ngl-link-all-data", "href"),
        Output("link-loading-placeholder-all-data", "children"),
        Input("data-table", "data"),
        Input("client-info-json", "data"),
    )
    def update_link_all_data(rows, info_cache):
        if rows is None or len(rows) == 0:
            sb = generate_statebuilder(info_cache, anno_layer="anno")
            return sb.render_state(None, return_as="url"), ""
        else:
            df = pd.DataFrame(rows)
            df["pt_position"] = df.apply(assemble_pt_position, axis=1)
            return generate_url_cell_types([], df, info_cache), ""

    pass