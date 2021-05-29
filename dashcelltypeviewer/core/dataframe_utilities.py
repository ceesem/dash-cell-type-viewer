import re
import numpy as np
from .config import *


def assemble_pt_position(row, prefix=""):
    return np.array(
        [
            row[f"{prefix}pt_position_x"],
            row[f"{prefix}pt_position_y"],
            row[f"{prefix}pt_position_z"],
        ]
    )


def stringify_root_ids(df, stringify_cols=None):
    if stringify_cols is None:
        stringify_cols = [col for col in df.columns if re.search("_root_id$", col)]
    for col in stringify_cols:
        df[col] = df[col].astype(str)
    return df


def process_dataframe(df):
    df["soma_depth_um"] = df["pt_position_y"].apply(
        lambda x: voxel_resolution[1] * x / 1000
    )
    df["num_anno"] = df.groupby("pt_root_id").transform("count")["pt_position_x"]
    return df