from __future__ import annotations
from typing import List
import panel as pn

from bencher.results.panel_result import PanelResult
from bencher.results.plotly_result import PlotlyResult
from bencher.results.holoview_result import HoloviewResult
from bencher.results.bench_result_base import EmptyContainer

# from bencher.results.heatmap_result import HeatMapResult

# from bencher.results.seaborn_result import SeabornResult


class BenchResult(PlotlyResult, HoloviewResult):

    """Contains the results of the benchmark and has methods to cast the results to various datatypes and graphical representations"""

    def __init__(self, bench_cfg) -> None:
        PlotlyResult.__init__(self, bench_cfg)
        HoloviewResult.__init__(self, bench_cfg)

    @staticmethod
    def default_plot_callbacks():
        return [
            HoloviewResult.to_bar,
            HoloviewResult.to_scatter_jitter,
            HoloviewResult.to_curve,
            HoloviewResult.to_line,
            HoloviewResult.to_heatmap,
            PlotlyResult.to_volume,
            PanelResult.to_video,
            PanelResult.to_panes,
        ]

    @staticmethod
    def plotly_callbacks():
        return [HoloviewResult.to_surface, PlotlyResult.to_volume]

    def to_auto(
        self,
        plot_list: List[callable] = None,
        remove_plots: List[callable] = None,
        **kwargs,
    ) -> List[pn.panel]:
        self.plt_cnt_cfg.print_debug = False

        if plot_list is None:
            plot_list = BenchResult.default_plot_callbacks()
        if remove_plots is not None:
            for p in remove_plots:
                plot_list.remove(p)

        row = EmptyContainer(pn.Row())
        for plot_callback in plot_list:
            if self.plt_cnt_cfg.print_debug:
                print(f"checking: {plot_callback.__name__}")
            # the callbacks are passed from the static class definition, so self needs to be passed before the plotting callback can be called
            row.append(plot_callback(self, **kwargs))

        self.plt_cnt_cfg.print_debug = True
        if len(row.pane) == 0:
            row.append(
                pn.pane.Markdown("No Plotters are able to represent these results", **kwargs)
            )
        return row.pane

    def to_auto_da(self):
        pass

    def to_auto_plots(self, **kwargs) -> List[pn.panel]:
        """Given the dataset result of a benchmark run, automatically dedeuce how to plot the data based on the types of variables that were sampled

        Args:
            bench_cfg (BenchCfg): Information on how the benchmark was sampled and the resulting data

        Returns:
            pn.pane: A panel containing plot results
        """
        plot_cols = pn.Column()
        plot_cols.append(self.to_sweep_summary(name="Plots View"))
        plot_cols.append(self.to_auto(**kwargs))
        plot_cols.append(self.bench_cfg.to_post_description())
        return plot_cols
