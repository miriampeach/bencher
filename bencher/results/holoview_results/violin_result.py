from __future__ import annotations
from typing import Optional
import panel as pn
import holoviews as hv
from param import Parameter
import xarray as xr

import hvplot.xarray  # noqa pylint: disable=duplicate-code,unused-import
import hvplot.pandas  # noqa pylint: disable=duplicate-code,unused-import
from bencher.results.bench_result_base import ReduceType

from bencher.plotting.plot_filter import VarRange
from bencher.variables.results import ResultVar

from bencher.results.holoview_results.holoview_result import HoloviewResult
from bencher.utils import params_to_str


class ViolinResult(HoloviewResult):
    """A class for creating violin plots from benchmark results.

    Violin plots combine aspects of box plots with kernel density plots, showing
    the distribution shape of the data. This class provides methods to generate
    these plots from benchmark data, which is particularly useful for visualizing
    the distribution of metrics across different configurations or repetitions.
    """

    def to_violin(
        self, result_var: Parameter = None, override: bool = True, **kwargs
    ) -> Optional[pn.panel]:
        """Generates a violin plot from benchmark data.

        This method applies filters to ensure the data is appropriate for a violin plot
        and then passes the filtered data to to_violin_ds for rendering.

        Args:
            result_var (Parameter, optional): The result variable to plot. If None, uses the default.
            override (bool, optional): Whether to override filter restrictions. Defaults to True.
            **kwargs: Additional keyword arguments passed to the plot rendering.

        Returns:
            Optional[pn.panel]: A panel containing the violin plot if data is appropriate,
                              otherwise returns filter match results.
        """
        return self.filter(
            self.to_violin_ds,
            float_range=VarRange(0, 0),
            cat_range=VarRange(0, None),
            repeats_range=VarRange(2, None),
            reduce=ReduceType.NONE,
            target_dimension=2,
            result_var=result_var,
            result_types=(ResultVar),
            override=override,
            **kwargs,
        )

    def to_violin_ds(self, dataset: xr.Dataset, result_var: Parameter, **kwargs) -> hv.Violin:
        """Creates a violin plot from the provided dataset.

        Given a filtered dataset, this method generates a violin plot visualization showing
        the distribution of values for a result variable, potentially grouped by a categorical variable.

        Args:
            dataset (xr.Dataset): The dataset containing benchmark results.
            result_var (Parameter): The result variable to plot.
            **kwargs: Additional keyword arguments passed to the violin plot options.

        Returns:
            hv.Violin: A HoloViews Violin plot of the benchmark data.
        """
        # Get the name of the result variable (which is the data we want to plot)
        var_name = result_var.name

        # Create plot title
        title = self.title_from_ds(dataset[var_name], result_var, **kwargs)

        # Convert dataset to dataframe for HoloViews
        df = dataset[var_name].to_dataframe().reset_index()

        # Get kdims from categorical variables
        kdims = params_to_str(self.plt_cnt_cfg.cat_vars)

        # Create the violin plot using HoloViews directly
        return hv.Violin(
            df,
            kdims=kdims,
            vdims=[var_name],
        ).opts(
            title=title,
            ylabel=f"{var_name} [{result_var.units}]",
            xrotation=30,  # Rotate x-axis labels by 30 degrees
            **kwargs,
        )
