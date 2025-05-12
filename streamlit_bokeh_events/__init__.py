from __future__ import annotations

import json
import os
from random import choices
from string import ascii_letters
from typing import Any, Dict, Optional

import streamlit.components.v1 as components
from bokeh.embed import json_item

_RELEASE = True  # flip to False when you want hot-reload at localhost:3001

if not _RELEASE:
    _component_func = components.declare_component(
        "streamlit_bokeh_events",
        url="http://localhost:3001",
    )
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend", "build")
    _component_func = components.declare_component(
        "streamlit_bokeh_events",
        path=build_dir,
    )


def streamlit_bokeh_events(
    *,
    bokeh_plot: Any,
    events: str = "",
    key: str,
    debounce_time: int = 1000,
    refresh_on_update: bool = True,
    override_height: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """Embed *bokeh_plot* and listen for custom JS events.

    Parameters
    ----------
    bokeh_plot
        Any Bokeh `Model` or `LayoutDOM` to embed.
    events
        Comma-separated list of custom event names to capture.
    key
        Mandatory Streamlit component key.
    debounce_time
        Milliseconds of silence before the event payload is sent to Python.
    refresh_on_update
        If *False*, the JS plot is not re-embedded on every rerun.
    override_height
        Fix the iframe height (pixels).  If ``None`` we use the plot’s own height.
    """
    div_id = "".join(choices(ascii_letters, k=16))
    fig_dict = json_item(bokeh_plot, div_id)
    json_figure = json.dumps(fig_dict)

    return _component_func(
        bokeh_plot=json_figure,
        events=events,
        key=key,
        _id=div_id,
        debounce_time=debounce_time,
        refresh_on_update=refresh_on_update,
        override_height=override_height,
        default=None,
    )


# -----------------------------------------------------------------------------#
# Demo block (runs only when you execute this file directly with _RELEASE=False)
# -----------------------------------------------------------------------------#
if not _RELEASE:  # pragma: no cover
    import streamlit as st
    import pandas as pd
    from bokeh.models import ColumnDataSource, CustomJS, DataTable, TableColumn
    from bokeh.plotting import figure

    st.set_page_config(layout="wide")

    df = pd.read_csv(
        "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"
    )

    # --- Column-select demo ---------------------------------------------------
    cds = ColumnDataSource(df)
    cds.selected.js_on_change(
        "indices",
        CustomJS(
            args=dict(source=cds),
            code="""
            document.dispatchEvent(
              new CustomEvent("INDEX_SELECT",
                              {detail: {data: source.selected.indices}}))
            """,
        ),
    )

    table = DataTable(
        source=cds,
        columns=[TableColumn(field=c, title=c) for c in df.columns],
        height=500,
    )

    col1, col2 = st.columns(2)

    with col1:
        res = streamlit_bokeh_events(
            bokeh_plot=table,
            events="INDEX_SELECT",
            key="tbl",
            refresh_on_update=False,
            debounce_time=0,
            override_height=500,
        )
        if res and res.get("INDEX_SELECT"):
            st.write(df.iloc[res["INDEX_SELECT"]["data"]])

    # --- Lasso-select demo ----------------------------------------------------
    df["color"] = df.species.map(
        {"setosa": "#583d72", "versicolor": "#9f5f80", "virginica": "#ffba93"}
    )
    plot_cds = ColumnDataSource(df)
    plot_cds.selected.js_on_change(
        "indices",
        CustomJS(
            args=dict(source=plot_cds),
            code="""
            document.dispatchEvent(
              new CustomEvent("LASSO_SELECT",
                              {detail: {data: source.selected.indices}}))
            """,
        ),
    )

    p = figure(tools="lasso_select,zoom_in")
    p.circle(
        "sepal_length",
        "sepal_width",
        color="color",
        size=10,
        alpha=0.6,
        line_color=None,
        source=plot_cds,
    )

    with col2:
        res2 = streamlit_bokeh_events(
            bokeh_plot=p,
            events="LASSO_SELECT",
            key="plot",
            refresh_on_update=False,
            debounce_time=0,
        )
        if res2 and res2.get("LASSO_SELECT"):
            st.write(df.iloc[res2["LASSO_SELECT"]["data"]])
