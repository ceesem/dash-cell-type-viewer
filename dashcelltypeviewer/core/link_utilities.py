from nglui import statebuilder
import pandas as pd
from seaborn import color_palette
from itertools import cycle


def image_source(info_cache):
    return info_cache["aligned_volume"]["image_source"]


def seg_source(info_cache):
    return info_cache["segmentation_source"]


def viewer_site(info_cache):
    return info_cache["viewer_site"]


def state_server(info_cache):
    return f"{info_cache['global_server']}/nglstate/api/v1/post"


def generate_statebuilder(
    info_cache,
    base_root_id=None,
    base_color="#ffffff",
    preselect_all=True,
    anno_column="post_pt_root_id",
    anno_layer="syns",
):
    img = statebuilder.ImageLayerConfig(
        image_source(info_cache), contrast_controls=True, black=0.35, white=0.65
    )
    if preselect_all:
        selected_ids_column = [anno_column]
    else:
        selected_ids_column = None
    if base_root_id is None:
        base_root_id = []
        base_color = [None]
    else:
        base_root_id = [base_root_id]
        base_color = [base_color]

    seg = statebuilder.SegmentationLayerConfig(
        seg_source(info_cache),
        selected_ids_column=selected_ids_column,
        fixed_ids=base_root_id,
        fixed_id_colors=base_color,
        alpha_3d=0.8,
    )

    points = statebuilder.PointMapper(
        "ctr_pt_position",
        linked_segmentation_column=anno_column,
        group_column=anno_column,
        set_position=True,
    )
    anno = statebuilder.AnnotationLayerConfig(
        anno_layer,
        mapping_rules=points,
        linked_segmentation_layer=seg.name,
        filter_by_segmentation=True,
    )
    sb = statebuilder.StateBuilder(
        [img, seg, anno],
        url_prefix=viewer_site(info_cache),
        state_server=state_server(info_cache),
    )
    return sb


def generate_url_cell_types(selected_rows, df, info_cache, palette="tab20"):
    # if selected_rows is None:
    # selected_rows = []
    if len(selected_rows) > 0 or selected_rows is None:
        df = df.iloc[selected_rows].reset_index(drop=True)
    cell_types = pd.unique(df["cell_type"])
    img = statebuilder.ImageLayerConfig(
        image_source(info_cache), contrast_controls=True, black=0.35, white=0.65
    )
    seg = statebuilder.SegmentationLayerConfig(
        seg_source(info_cache),
        alpha_3d=0.8,
    )
    sbs = [
        statebuilder.StateBuilder(
            [img, seg],
            state_server=state_server(info_cache),
        )
    ]
    dfs = [None]
    colors = color_palette(palette).as_hex()
    for ct, clr in zip(cell_types, cycle(colors)):
        anno = statebuilder.AnnotationLayerConfig(
            ct,
            color=clr,
            linked_segmentation_layer=seg.name,
            mapping_rules=statebuilder.PointMapper(
                "pt_position",
                linked_segmentation_column="pt_root_id",
                set_position=True,
            ),
        )
        sbs.append(
            statebuilder.StateBuilder(
                [anno],
                state_server=state_server(info_cache),
            )
        )
        dfs.append(df.query("cell_type == @ct"))
    csb = statebuilder.ChainedStateBuilder(sbs)
    return csb.render_state(dfs, return_as="url")
