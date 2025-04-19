from __future__ import annotations
from typing import Optional, List
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
    """

    def to_scatter_jitter(
        self,
        override: bool = False,
        **kwargs,  # pylint: disable=unused-argument
    ) -> List[hv.Scatter]:
        """Creates jittered scatter plots for all result variables.

        This method generates scatter plots with jittering to better visualize
        overlapping data points. It creates one scatter plot for each result variable.

        Args:
            override (bool, optional): Whether to override filter restrictions. Defaults to False.
            **kwargs: Additional keyword arguments passed to the scatter plot options.

        Returns:
            List[hv.Scatter]: A list of scatter plots, one for each result variable.
        """
        return self.overlay_plots(
            partial(self.to_scatter_jitter_single, override=override, **kwargs)
        )

    def to_scatter_jitter_single(
        self, result_var: Parameter, override: bool = True, **kwargs
    ) -> Optional[hv.Scatter]:
        """Creates a jittered scatter plot for a single result variable.

        This method generates a scatter plot with jittering for a specific result variable,
        allowing better visualization of overlapping points, particularly useful when
        displaying multiple repetitions of benchmark results.

        Args:
            result_var (Parameter): The result variable to plot.
            override (bool, optional): Whether to override filter restrictions. Defaults to True.
            **kwargs: Additional keyword arguments passed to the scatter plot options.

        Returns:
            Optional[hv.Scatter]: A scatter plot if data matches criteria,
                               otherwise returns filter match results.
        """
        matches = PlotFilter(
            float_range=VarRange(0, 0),
            cat_range=VarRange(0, None),
            repeats_range=VarRange(2, None),
            input_range=VarRange(1, None),
        ).matches_result(self.plt_cnt_cfg, "to_scatter_jitter", override)
        if matches.overall:
            ds = self.to_hv_dataset(ReduceType.NONE)
            pt = (
                ds.to(hv.Scatter, vdims=[result_var.name], label=result_var.name)
                .opts(jitter=0.1, show_legend=False, title=self.to_plot_title(), **kwargs)
                .overlay("repeat")
            )
            return pt
        return matches.to_panel()

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
