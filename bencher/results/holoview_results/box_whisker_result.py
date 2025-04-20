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

from bokeh.sampledata.autompg import autompg as df


class BoxWhiskerResult(HoloviewResult):
    """A class for creating box and whisker plots from benchmark results.

    Box and whisker plots are useful for visualizing the distribution of data,
    including the median, quartiles, and potential outliers. This class provides
    methods to generate these plots from benchmark data, particularly useful for
    comparing distributions across different categorical variables or between
    different repetitions of the same benchmark.
    """

    def to_boxplot(
        self, result_var: Parameter = None, override: bool = True, **kwargs
    ) -> Optional[pn.panel]:
        """Generates a box and whisker plot from benchmark data.

        This method applies filters to ensure the data is appropriate for a box plot
        and then passes the filtered data to to_boxplot_ds for rendering.

        Args:
            result_var (Parameter, optional): The result variable to plot. If None, uses the default.
            override (bool, optional): Whether to override filter restrictions. Defaults to True.
            **kwargs: Additional keyword arguments passed to the plot rendering.

        Returns:
            Optional[pn.panel]: A panel containing the box plot if data is appropriate,
                              otherwise returns filter match results.
        """
        return self.filter(
            self.to_boxplot_ds,
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

    def to_boxplot_ds(self, dataset: xr.Dataset, result_var: Parameter, **kwargs) -> hv.BoxWhisker:
        """Creates a box and whisker plot from the provided dataset.

        Given a filtered dataset, this method generates a box and whisker visualization showing
        the distribution of values for a result variable, potentially grouped by a categorical variable.

        Args:
            dataset (xr.Dataset): The dataset containing benchmark results.
            result_var (Parameter): The result variable to plot.
            **kwargs: Additional keyword arguments passed to the box plot options.

        Returns:
            hv.BoxWhisker: A HoloViews BoxWhisker plot of the benchmark data.
        """
        # Get the name of the result variable (which is the data we want to plot)
        var_name = result_var.name

        # Create plot title
        title = self.title_from_ds(dataset[var_name], result_var, **kwargs)

        df = dataset[var_name].to_dataframe().reset_index()

        # Create a box plot directly using the HoloViews interface
        # We'll group by all dimensions except 'repeat'
        data = []
        cat_dims = []

        # Find the categorical dimension names that we'll use for grouping
        for dim in dataset[var_name].dims:
            if dim != "repeat" and isinstance(
                dataset[var_name].coords[dim].values[0], (str, bytes)
            ):
                cat_dims.append(dim)

        # If we have categorical dimensions, create a box for each category
        if cat_dims:
            # Convert to dataframe format that HoloViews expects
            df = dataset[var_name].to_dataframe().reset_index()
            # Only keep the categorical dimensions and the value
            box_df = df[cat_dims + [var_name]]
            # Create BoxWhisker using the dataframe
            box_whisker = hv.BoxWhisker(box_df, kdims=cat_dims, vdims=[var_name])
        else:
            # Without categorical dimensions, create a single box
            values = dataset[var_name].values.flatten()
            box_whisker = hv.BoxWhisker(values, vdims=[var_name])

        # Apply styling options
        ylabel = f"{var_name}"
        if hasattr(result_var, "units") and result_var.units:
            ylabel += f" [{result_var.units}]"

        box_whisker = box_whisker.opts(
            title=title, ylabel=ylabel, box_fill_color="lightblue", **kwargs
        )

        return box_whisker
