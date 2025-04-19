from __future__ import annotations
from typing import Optional, List
import panel as pn
import holoviews as hv
from param import Parameter
from functools import partial

import hvplot.xarray  # noqa pylint: disable=duplicate-code,unused-import
import hvplot.pandas  # noqa pylint: disable=duplicate-code,unused-import
from bencher.results.bench_result_base import ReduceType

from bencher.plotting.plot_filter import VarRange, PlotFilter


from bencher.results.holoview_results.holoview_result import HoloviewResult


class ScatterResult(HoloviewResult):
    """A class for creating scatter plots from benchmark results.

    Scatter plots are useful for visualizing the distribution of individual data points
    and identifying patterns, clusters, or outliers. This class provides methods to
    generate scatter plots with jittering capabilities to better visualize overlapping
    points, particularly useful for displaying benchmark results across multiple repetitions.

    Methods include:
    - to_scatter_jitter: Creates scatter plots with jittering for better visualization of overlapping points
    - to_scatter: Creates standard scatter plots that can be grouped by categorical variables
    """

    def to_scatter_jitter(
        self,
        override: bool = False,
        **kwargs,  # pylint: disable=unused-argument
    ) -> List[hv.Scatter]:
        return self.overlay_plots(
            partial(self.to_scatter_jitter_single, override=override, **kwargs)
        )

    def to_scatter_jitter_single(
        self, result_var: Parameter, override: bool = True, **kwargs
    ) -> Optional[hv.Scatter]:
        matches = PlotFilter(
            float_range=VarRange(0, 0),
            cat_range=VarRange(0, None),
            repeats_range=VarRange(2, None),
            input_range=VarRange(1, None),
        ).matches_result(self.plt_cnt_cfg, "to_scatter_jitter", override)
        if matches.overall:
            ds = self.to_hv_dataset(ReduceType.NONE)
            return (
                ds.to(hv.Scatter, vdims=[result_var.name], label=result_var.name)
                .opts(jitter=0.1, show_legend=False, title=self.to_plot_title(), **kwargs)
                .overlay("repeat")
            )
        return matches.to_panel()

    def to_scatter(self, override: bool = True, **kwargs) -> Optional[pn.panel]:
        match_res = PlotFilter(
            float_range=VarRange(0, 0),
            cat_range=VarRange(0, None),
            repeats_range=VarRange(1, 1),
        ).matches_result(self.plt_cnt_cfg, "to_hvplot_scatter", override=override)
        if match_res.overall:
            hv_ds = self.to_hv_dataset(ReduceType.SQUEEZE)
            by = None
            subplots = False
            if self.plt_cnt_cfg.cat_cnt > 1:
                by = [v.name for v in self.bench_cfg.input_vars[1:]]
                subplots = False
            return hv_ds.data.hvplot.scatter(by=by, subplots=subplots, **kwargs).opts(
                title=self.to_plot_title()
            )
        return match_res.to_panel(**kwargs)

    # def to_scatter_jitter(self, **kwargs) -> Optional[hv.Scatter]:
    #     matches = PlotFilter(
    #         float_range=VarRange(0, 0),
    #         cat_range=VarRange(0, None),
    #         repeats_range=VarRange(2, None),
    #         input_range=VarRange(1, None),
    #     ).matches_result(self.plt_cnt_cfg, "to_scatter_jitter")
    #     if matches.overall:
    #         hv_ds = self.to_hv_dataset(ReduceType.NONE)

    #         by = None
    #         groupby = None
    #         subplots=False
    #         if self.plt_cnt_cfg.cat_cnt > 1:
    #             by = [v.name for v in self.bench_cfg.all_vars[1:]]
    #             subplots=False
    #         return hv_ds.data.hvplot.scatter(by=by,subplots=subplots, **kwargs).opts(title=self.to_plot_title())

    #         # pt = (
    #         #     hv_ds.to(hv.Scatter)
    #         #     .opts(jitter=0.1)
    #         #     .overlay("repeat")
    #         #     .opts(show_legend=False, title=self.to_plot_title(), **kwargs)
    #         # )
    #         # return pt
    #     return matches.to_panel()

    # def to_scatter_jitter_multi(self, **kwargs) -> Optional[hv.Scatter]:
    #     matches = PlotFilter(
    #         float_range=VarRange(0, 0),
    #         cat_range=VarRange(0, None),
    #         repeats_range=VarRange(2, None),
    #         input_range=VarRange(1, None),
    #     ).matches_result(self.plt_cnt_cfg, "to_scatter_jitter")
    #     if matches.overall:
    #         hv_dataset = self.to_hv_dataset(ReduceType.NONE)

    #         print("KDIMS",hv_dataset.kdims)
    #         # hv_dataset.kdims =[hv_dataset.kdims[2],hv_dataset.kdims[1],hv_dataset.kdims[0]]
    #         # print("KDIMS",hv_dataset.kdims)

    #         # exit()
    #         cb = partial(self.to_scatter_jitter_da, **kwargs)
    #         return self.to_panes_multi_panel(hv_dataset, None, plot_callback=cb, target_dimension=3)
    #     return matches.to_panel()

    # def to_scatter_jitter_da(self, ds: xr.Dataset, **kwargs) -> Optional[hv.Scatter]:
    #     matches = PlotFilter(
    #         float_range=VarRange(0, 0),
    #         cat_range=VarRange(0, None),
    #         repeats_range=VarRange(2, None),
    #         input_range=VarRange(1, None),
    #     ).matches_result(self.plt_cnt_cfg, "to_scatter_jitter")
    #     if matches.overall:

    #         print("DA IN",da)
    #         da = self.to_hv_dataset(ReduceType.NONE)
    #         hvds = hv.Dataset(da)
    #         # return None

    #         # print("DA FRESH",da)
    #         result_var = self.bench_cfg.result_vars[0]

    #         print(hvds.data.sizes)
    #         print("repeat" in hvds.data.sizes)
    #         # if "repeat" in hvds.data.sizes:
    #         # try:
    #         #     pt = (
    #         #         hvds.to(hv.Scatter)
    #         #         .opts(jitter=0.1)
    #         #         # .overlay()
    #         #         .overlay("repeat")
    #         #         .opts(show_legend=False, title=self.to_plot_title(), clabel=result_var.name, **kwargs)
    #         #     )
    #         # except:
    #         pt = (
    #             hvds.to(hv.Scatter)
    #             .opts(jitter=0.1)
    #             # .overlay()
    #             # .overlay("repeat")
    #             .opts(show_legend=False, title=self.to_plot_title(), clabel=result_var.name, **kwargs)
    #         )
    #         return pt
    #     return matches.to_panel()

    # def to_scatter_jitter(
    #     self, result_var: Parameter = None, override: bool = True, **kwargs
    # ) -> Optional[pn.panel]:
    #     return self.filter(
    #         self.to_scatter_ds,
    #         float_range=VarRange(0, 0),
    #         cat_range=VarRange(0, None),
    #         repeats_range=VarRange(2, None),
    #         reduce=ReduceType.NONE,
    #         target_dimension=2,
    #         result_var=result_var,
    #         result_types=(ResultVar),
    #         override=override,
    #         **kwargs,
    #     )

    # def to_scatter_ds(self, dataset: xr.Dataset, result_var: Parameter, **kwargs) -> hv.Scatter:
    #     by = None
    #     if self.plt_cnt_cfg.cat_cnt >= 2:
    #         by = self.plt_cnt_cfg.cat_vars[1].name
    #     # print(dataset)
    #     da_plot = dataset[result_var.name]
    #     # da_plot = dataset
    #     # print(da_plot)
    #     print("by", by)
    #     title = self.title_from_ds(da_plot, result_var, **kwargs)
    #     time_widget_args = self.time_widget(title)
    #     print(da_plot)
    #     # return da_plot.hvplot.box(by=by, **time_widget_args, **kwargs)
    #     # return da_plot.hvplot.box( **time_widget_args, **kwargs)
    #     return da_plot.hvplot.scatter(
    #         y=result_var.name, x="repeat", by=by, **time_widget_args, **kwargs
    #     ).opts(jitter=0.1)
