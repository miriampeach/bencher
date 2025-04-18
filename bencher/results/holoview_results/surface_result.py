from __future__ import annotations
import logging
from typing import Optional
import panel as pn
import holoviews as hv
from param import Parameter
import hvplot.xarray  # noqa pylint: disable=duplicate-code,unused-import
import xarray as xr

from bencher.results.bench_result_base import ReduceType
from bencher.plotting.plot_filter import PlotFilter, VarRange
from bencher.variables.results import ResultVar
from bencher.results.holoview_results.holoview_result import HoloviewResult


class SurfaceResult(HoloviewResult):
    def to_surface(
        self, result_var: Parameter = None, override: bool = True, **kwargs
    ) -> Optional[pn.pane.Pane]:
        return self.filter(
            self.to_surface_ds,
            float_range=VarRange(2, None),
            cat_range=VarRange(0, None),
            input_range=VarRange(1, None),
            reduce=ReduceType.REDUCE,
            target_dimension=2,
            result_var=result_var,
            result_types=(ResultVar),
            override=override,
            **kwargs,
        )

    def to_surface_ds(
        self,
        dataset: xr.Dataset,
        result_var: Parameter,
        override: bool = True,
        alpha: float = 0.3,
        **kwargs,
    ) -> Optional[pn.panel]:
        """Given a benchCfg generate a 2D surface plot

        Args:
            result_var (Parameter): result variable to plot

        Returns:
            pn.pane.holoview: A 2d surface plot as a holoview in a pane
        """
        matches_res = PlotFilter(
            float_range=VarRange(2, 2),
            cat_range=VarRange(0, None),
            vector_len=VarRange(1, 1),
            result_vars=VarRange(1, 1),
        ).matches_result(self.plt_cnt_cfg, "to_surface_hv", override)
        if matches_res.overall:
            # xr_cfg = plot_float_cnt_2(self.plt_cnt_cfg, result_var)

            # TODO a warning suggests setting this parameter, but it does not seem to help as expected, leaving here to fix in the future
            # hv.config.image_rtol = 1.0

            mean = dataset[result_var.name]

            hvds = hv.Dataset(dataset[result_var.name])

            x = self.plt_cnt_cfg.float_vars[0]
            y = self.plt_cnt_cfg.float_vars[1]

            try:
                surface = hvds.to(hv.Surface, vdims=[result_var.name])
                surface = surface.opts(colorbar=True)
            except Exception as e:  # pylint: disable=broad-except
                logging.warning(e)

            if self.bench_cfg.repeats > 1:
                std_dev = dataset[f"{result_var.name}_std"]

                upper = mean + std_dev
                upper.name = result_var.name

                lower = mean - std_dev
                lower.name = result_var.name

                surface *= (
                    hv.Dataset(upper)
                    .to(hv.Surface)
                    .opts(alpha=alpha, colorbar=False, backend="plotly")
                )
                surface *= (
                    hv.Dataset(lower)
                    .to(hv.Surface)
                    .opts(alpha=alpha, colorbar=False, backend="plotly")
                )

            surface = surface.opts(
                zlabel=f"{result_var.name} [{result_var.units}]",
                title=f"{result_var.name} vs ({x.name} and {y.name})",
                backend="plotly",
                **kwargs,
            )

            if self.bench_cfg.render_plotly:
                hv.extension("plotly")
                out = surface
            else:
                # using render disabled the holoviews sliders :(
                out = hv.render(surface, backend="plotly")
            return pn.Column(out, name="surface_hv")

        return matches_res.to_panel()
