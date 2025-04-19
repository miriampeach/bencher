from __future__ import annotations
from typing import List, Optional
import panel as pn
import holoviews as hv
from param import Parameter
from functools import partial
import hvplot.xarray  # noqa pylint: disable=duplicate-code,unused-import
import xarray as xr

from bencher.utils import (
    get_nearest_coords1D,
)
from bencher.results.bench_result_base import ReduceType
from bencher.plotting.plot_filter import VarRange
from bencher.variables.results import ResultVar
from bencher.results.holoview_results.holoview_result import HoloviewResult


class LineResult(HoloviewResult):
    """A class for creating line plot visualizations from benchmark results.

    Line plots are effective for visualizing trends in data over a continuous variable.
    This class provides methods to generate interactive line plots from benchmark data,
    with options for adding interactive tap functionality to display detailed information
    about specific data points.
    """

    def to_line(
        self,
        result_var: Parameter = None,
        tap_var=None,
        tap_container: pn.pane.panel = None,
        target_dimension=2,
        override: bool = True,
        use_tap: bool = None,
        **kwargs,
    ) -> Optional[pn.panel]:
        if tap_var is None:
            tap_var = self.plt_cnt_cfg.panel_vars
        elif not isinstance(tap_var, list):
            tap_var = [tap_var]

        if len(tap_var) == 0 or self.plt_cnt_cfg.inputs_cnt > 1 or not use_tap:
            line_cb = self.to_line_ds
        else:
            line_cb = partial(
                self.to_line_tap_ds, result_var_plots=tap_var, container=tap_container
            )

        return self.filter(
            line_cb,
            float_range=VarRange(1, 1),
            cat_range=VarRange(0, None),
            repeats_range=VarRange(1, 1),
            panel_range=VarRange(0, None),
            reduce=ReduceType.SQUEEZE,
            target_dimension=target_dimension,
            result_var=result_var,
            result_types=(ResultVar),
            override=override,
            **kwargs,
        )

    def to_line_ds(self, dataset: xr.Dataset, result_var: Parameter, **kwargs):
        x = self.plt_cnt_cfg.float_vars[0].name
        by = None
        if self.plt_cnt_cfg.cat_cnt >= 1:
            by = self.plt_cnt_cfg.cat_vars[0].name
        da_plot = dataset[result_var.name]
        title = self.title_from_ds(da_plot, result_var, **kwargs)
        time_widget_args = self.time_widget(title)
        return da_plot.hvplot.line(x=x, by=by, **time_widget_args, **kwargs)

    def to_line_tap_ds(
        self,
        dataset: xr.Dataset,
        result_var: Parameter,
        result_var_plots: List[Parameter] = None,
        container: pn.pane.panel = pn.pane.panel,
        **kwargs,
    ) -> pn.Row:
        htmap = self.to_line_ds(dataset, result_var).opts(tools=["hover"], **kwargs)
        result_var_plots, cont_instances = self.setup_results_and_containers(
            result_var_plots, container
        )
        title = pn.pane.Markdown("Selected: None")

        state = dict(x=None, y=None, update=False)

        def tap_plot_line(x, y):  # pragma: no cover
            # print(f"{x},{y}")
            # print(dataset)

            # xv = self.bench_cfg.input_vars[0].name
            # yv = self.bench_cfg.input_vars[1].name

            # x_nearest_new = get_nearest_coords1D(
            #     x, dataset.coords[self.bench_cfg.input_vars[0].name].data
            # )
            # y_nearest_new = get_nearest_coords1D(
            #     y, dataset.coords[self.bench_cfg.input_vars[1].name].data
            # )

            # kwargs = {xv: x, yv: y}

            # nearest = get_nearest_coords(dataset, **kwargs)
            # print(nearest)

            x_nearest_new = get_nearest_coords1D(
                x, dataset.coords[self.bench_cfg.input_vars[0].name].data
            )

            if x_nearest_new != state["x"]:
                state["x"] = x_nearest_new
                state["update"] = True

            if self.plt_cnt_cfg.inputs_cnt > 1:
                y_nearest_new = get_nearest_coords1D(
                    y, dataset.coords[self.bench_cfg.input_vars[1].name].data
                )
                if y_nearest_new != state["y"]:
                    state["y"] = y_nearest_new
                    state["update"] = True

            if state["update"]:
                kdims = {}
                kdims[self.bench_cfg.input_vars[0].name] = state["x"]
                if self.plt_cnt_cfg.inputs_cnt > 1:
                    kdims[self.bench_cfg.input_vars[1].name] = state["y"]

                if hasattr(htmap, "current_key"):
                    for d, k in zip(htmap.kdims, htmap.current_key):
                        kdims[d.name] = k
                for rv, cont in zip(result_var_plots, cont_instances):
                    ds = dataset[rv.name]
                    val = ds.sel(**kdims)
                    item = self.zero_dim_da_to_val(val)
                    title.object = "Selected: " + ", ".join([f"{k}:{v}" for k, v in kdims.items()])
                    cont.object = item
                    if hasattr(cont, "autoplay"):  # container is a video, set to autoplay
                        cont.paused = False
                        cont.time = 0
                        cont.loop = True
                        cont.autoplay = True
                state["update"] = False

        def on_exit(x, y):  # pragma: no cover # pylint: disable=unused-argument
            state["update"] = True

        htmap_posxy = hv.streams.PointerXY(source=htmap)
        htmap_posxy.add_subscriber(tap_plot_line)
        ls = hv.streams.MouseLeave(source=htmap)
        ls.add_subscriber(on_exit)
        bound_plot = pn.Column(title, *cont_instances)
        return pn.Row(htmap, bound_plot)
