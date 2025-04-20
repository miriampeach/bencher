from __future__ import annotations
from typing import Optional, Callable, Any
import panel as pn
import holoviews as hv
from param import Parameter
import xarray as xr

from bencher.results.bench_result_base import ReduceType
from bencher.plotting.plot_filter import VarRange
from bencher.variables.results import ResultVar
from bencher.results.holoview_results.holoview_result import HoloviewResult
from bencher.utils import params_to_str


class DistributionResult(HoloviewResult):
    """A base class for creating distribution plots (violin, box-whisker) from benchmark results.

    This class provides common functionality for various distribution plot types that show
    the distribution shape of the data. Child classes implement specific plot types
    (e.g., violin plots, box and whisker plots) but share filtering and data preparation logic.
    """

    def to_distribution_plot(
        self,
        plot_method: Callable[[xr.Dataset, Parameter, Any], hv.Element],
        result_var: Parameter = None,
        override: bool = True,
        **kwargs,
    ) -> Optional[pn.panel]:
        """Generates a distribution plot from benchmark data.

        This method applies filters to ensure the data is appropriate for distribution plots
        and then passes the filtered data to the specified plot method for rendering.

        Args:
            plot_method: The method to use for creating the specific plot type
            result_var (Parameter, optional): The result variable to plot. If None, uses the default.
            override (bool, optional): Whether to override filter restrictions. Defaults to True.
            **kwargs: Additional keyword arguments passed to the plot rendering.

        Returns:
            Optional[pn.panel]: A panel containing the plot if data is appropriate,
                              otherwise returns filter match results.
        """
        return self.filter(
            plot_method,
            float_range=VarRange(0, 0),
            cat_range=VarRange(0, None),
            repeats_range=VarRange(2, None),
            reduce=ReduceType.NONE,
            target_dimension=self.plt_cnt_cfg.cat_cnt + 1,  # +1 cos we have a repeats dimension
            result_var=result_var,
            result_types=(ResultVar),
            override=override,
            **kwargs,
        )

    def _plot_distribution(
        self, dataset: xr.Dataset, result_var: Parameter, plot_class: hv.Selection1DExpr, **kwargs
    ) -> tuple[str, str, Any]:
        """Prepares data for distribution plots.

        This method handles common operations needed for all distribution plot types.

        Args:
            dataset (xr.Dataset): The dataset containing benchmark results.
            result_var (Parameter): The result variable to plot.
            **kwargs: Additional keyword arguments.

        Returns:
            tuple: (var_name, title, dataframe, kdims) with prepared data for plotting
        """
        # Get the name of the result variable (which is the data we want to plot)
        var_name = result_var.name

        # Create plot title
        title = self.title_from_ds(dataset[var_name], result_var, **kwargs)

        # Convert dataset to dataframe for HoloViews
        df = dataset[var_name].to_dataframe().reset_index()
        kdims = params_to_str(self.plt_cnt_cfg.cat_vars)
        return plot_class(
            df,
            kdims=kdims,
            vdims=[var_name],
        ).opts(
            title=title,
            ylabel=f"{var_name} [{result_var.units}]",
            xrotation=30,  # Rotate x-axis labels by 30 degrees
            **kwargs,
        )
