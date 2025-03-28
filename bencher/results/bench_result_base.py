import logging
from typing import List, Any, Tuple, Optional
from enum import Enum, auto
import xarray as xr
from param import Parameter
import holoviews as hv
from functools import partial
from bencher.utils import int_to_col, color_tuple_to_css

from bencher.variables.parametrised_sweep import ParametrizedSweep
from bencher.variables.results import OptDir
from copy import deepcopy
from bencher.results.optuna_result import OptunaResult
from bencher.variables.results import ResultVar
from bencher.results.float_formatter import FormatFloat
from bencher.plotting.plot_filter import VarRange, PlotFilter
import panel as pn


# todo add plugins
# https://gist.github.com/dorneanu/cce1cd6711969d581873a88e0257e312
# https://kaleidoescape.github.io/decorated-plugins/


class ReduceType(Enum):
    AUTO = auto()  # automatically determine the best way to reduce the dataset
    SQUEEZE = auto()  # remove any dimensions of length 1
    REDUCE = auto()  # get the mean and std dev of the the "repeat" dimension
    NONE = auto()  # don't reduce


class EmptyContainer:
    """A wrapper for list like containers that only appends if the item is not None"""

    def __init__(self, pane) -> None:
        self.pane = pane

    def append(self, child):
        if child is not None:
            self.pane.append(child)

    def get(self):
        return self.pane if len(self.pane) > 0 else None


class BenchResultBase(OptunaResult):
    def result_samples(self) -> int:
        """The number of samples in the results dataframe"""
        return self.ds.count()

    def to_hv_dataset(
        self, reduce: ReduceType = ReduceType.AUTO, result_var: ResultVar = None
    ) -> hv.Dataset:
        """Generate a holoviews dataset from the xarray dataset.

        Args:
            reduce (ReduceType, optional): Optionally perform reduce options on the dataset.  By default the returned dataset will calculate the mean and standard devation over the "repeat" dimension so that the dataset plays nicely with most of the holoviews plot types.  Reduce.Sqeeze is used if there is only 1 repeat and you want the "reduce" variable removed from the dataset. ReduceType.None returns an unaltered dataset. Defaults to ReduceType.AUTO.

        Returns:
            hv.Dataset: results in the form of a holoviews dataset
        """

        if reduce == ReduceType.NONE:
            kdims = [i.name for i in self.bench_cfg.all_vars]
            return hv.Dataset(self.to_dataset(reduce, result_var), kdims=kdims)
        return hv.Dataset(self.to_dataset(reduce, result_var))

    def to_dataset(
        self, reduce: ReduceType = ReduceType.AUTO, result_var: ResultVar = None
    ) -> xr.Dataset:
        """Generate a summarised xarray dataset.

        Args:
            reduce (ReduceType, optional): Optionally perform reduce options on the dataset.  By default the returned dataset will calculate the mean and standard devation over the "repeat" dimension so that the dataset plays nicely with most of the holoviews plot types.  Reduce.Sqeeze is used if there is only 1 repeat and you want the "reduce" variable removed from the dataset. ReduceType.None returns an unaltered dataset. Defaults to ReduceType.AUTO.

        Returns:
            xr.Dataset: results in the form of an xarray dataset
        """
        if reduce == ReduceType.AUTO:
            reduce = ReduceType.REDUCE if self.bench_cfg.repeats > 1 else ReduceType.SQUEEZE

        ds = self.ds if result_var is None else self.ds[result_var.name]

        match (reduce):
            case ReduceType.REDUCE:
                ds_reduce_mean = ds.mean(dim="repeat", keep_attrs=True)
                ds_reduce_std = ds.std(dim="repeat", keep_attrs=True)

                for v in ds_reduce_mean.data_vars:
                    ds_reduce_mean[f"{v}_std"] = ds_reduce_std[v]
                return ds_reduce_mean
            case ReduceType.SQUEEZE:
                return ds.squeeze(drop=True)
            case _:
                return ds

    def get_optimal_vec(
        self,
        result_var: ParametrizedSweep,
        input_vars: List[ParametrizedSweep],
    ) -> List[Any]:
        """Get the optimal values from the sweep as a vector.

        Args:
            result_var (bch.ParametrizedSweep): Optimal values of this result variable
            input_vars (List[bch.ParametrizedSweep]): Define which input vars values are returned in the vector

        Returns:
            List[Any]: A vector of optimal values for the desired input vector
        """

        da = self.get_optimal_value_indices(result_var)
        output = []
        for iv in input_vars:
            if da.coords[iv.name].values.size == 1:
                # https://stackoverflow.com/questions/773030/why-are-0d-arrays-in-numpy-not-considered-scalar
                # use [()] to convert from a 0d numpy array to a scalar
                output.append(da.coords[iv.name].values[()])
            else:
                logging.warning(f"values size: {da.coords[iv.name].values.size}")
                output.append(max(da.coords[iv.name].values[()]))
            logging.info(f"Maximum value of {iv.name}: {output[-1]}")
        return output

    def get_optimal_value_indices(self, result_var: ParametrizedSweep) -> xr.DataArray:
        """Get an xarray mask of the values with the best values found during a parameter sweep

        Args:
            result_var (bch.ParametrizedSweep): Optimal value of this result variable

        Returns:
            xr.DataArray: xarray mask of optimal values
        """
        result_da = self.ds[result_var.name]
        if result_var.direction == OptDir.maximize:
            opt_val = result_da.max()
        else:
            opt_val = result_da.min()
        indicies = result_da.where(result_da == opt_val, drop=True).squeeze()
        logging.info(f"optimal value of {result_var.name}: {opt_val.values}")
        return indicies

    def get_optimal_inputs(
        self,
        result_var: ParametrizedSweep,
        keep_existing_consts: bool = True,
        as_dict: bool = False,
    ) -> Tuple[ParametrizedSweep, Any] | dict[ParametrizedSweep, Any]:
        """Get a list of tuples of optimal variable names and value pairs, that can be fed in as constant values to subsequent parameter sweeps

        Args:
            result_var (bch.ParametrizedSweep): Optimal values of this result variable
            keep_existing_consts (bool): Include any const values that were defined as part of the parameter sweep
            as_dict (bool): return value as a dictionary

        Returns:
            Tuple[bch.ParametrizedSweep, Any]|[ParametrizedSweep, Any]: Tuples of variable name and optimal values
        """
        da = self.get_optimal_value_indices(result_var)
        if keep_existing_consts:
            output = deepcopy(self.bench_cfg.const_vars)
        else:
            output = []

        for iv in self.bench_cfg.input_vars:
            # assert da.coords[iv.name].values.size == (1,)
            if da.coords[iv.name].values.size == 1:
                # https://stackoverflow.com/questions/773030/why-are-0d-arrays-in-numpy-not-considered-scalar
                # use [()] to convert from a 0d numpy array to a scalar
                output.append((iv, da.coords[iv.name].values[()]))
            else:
                logging.warning(f"values size: {da.coords[iv.name].values.size}")
                output.append((iv, max(da.coords[iv.name].values[()])))

            logging.info(f"Maximum value of {iv.name}: {output[-1][1]}")
        if as_dict:
            return dict(output)
        return output

    def describe_sweep(self):
        return self.bench_cfg.describe_sweep()

    def get_best_holomap(self, name: str = None):
        return self.get_hmap(name)[self.get_best_trial_params(True)]

    def get_hmap(self, name: str = None):
        try:
            if name is None:
                name = self.result_hmaps[0].name
            if name in self.hmaps:
                return self.hmaps[name]
        except Exception as e:
            raise RuntimeError(
                "You are trying to plot a holomap result but it is not in the result_vars list.  Add the holomap to the result_vars list"
            ) from e
        return None

    def to_plot_title(self) -> str:
        if len(self.bench_cfg.input_vars) > 0 and len(self.bench_cfg.result_vars) > 0:
            return f"{self.bench_cfg.result_vars[0].name} vs {self.bench_cfg.input_vars[0].name}"
        return ""

    def title_from_ds(self, dataset: xr.Dataset, result_var: Parameter, **kwargs):
        if "title" in kwargs:
            return kwargs["title"]

        if isinstance(dataset, xr.DataArray):
            tit = [dataset.name]
            for d in dataset.dims:
                tit.append(d)
        else:
            tit = [result_var.name]
            tit.extend(list(dataset.sizes))

        return " vs ".join(tit)

    def get_results_var_list(self, result_var: ParametrizedSweep = None) -> List[ResultVar]:
        return self.bench_cfg.result_vars if result_var is None else [result_var]

    def map_plots(
        self,
        plot_callback: callable,
        result_var: ParametrizedSweep = None,
        row: EmptyContainer = None,
    ) -> Optional[pn.Row]:
        if row is None:
            row = EmptyContainer(pn.Row(name=self.to_plot_title()))
        for rv in self.get_results_var_list(result_var):
            row.append(plot_callback(rv))
        return row.get()

    def map_plot_panes(
        self,
        plot_callback: callable,
        hv_dataset: hv.Dataset = None,
        target_dimension: int = 2,
        result_var: ResultVar = None,
        result_types=None,
        **kwargs,
    ) -> Optional[pn.Row]:
        if hv_dataset is None:
            hv_dataset = self.to_hv_dataset()
        row = EmptyContainer(pn.Row())
        for rv in self.get_results_var_list(result_var):
            if result_types is None or isinstance(rv, result_types):
                row.append(
                    self.to_panes_multi_panel(
                        hv_dataset,
                        rv,
                        plot_callback=partial(plot_callback, **kwargs),
                        target_dimension=target_dimension,
                    )
                )
        return row.get()

    def filter(
        self,
        plot_callback: callable,
        plot_filter=None,
        float_range: VarRange = VarRange(0, None),
        cat_range: VarRange = VarRange(0, None),
        vector_len: VarRange = VarRange(1, 1),
        result_vars: VarRange = VarRange(1, 1),
        panel_range: VarRange = VarRange(0, 0),
        repeats_range: VarRange = VarRange(1, None),
        input_range: VarRange = VarRange(1, None),
        reduce: ReduceType = ReduceType.AUTO,
        target_dimension: int = 2,
        result_var: ResultVar = None,
        result_types=None,
        **kwargs,
    ):
        plot_filter = PlotFilter(
            float_range=float_range,
            cat_range=cat_range,
            vector_len=vector_len,
            result_vars=result_vars,
            panel_range=panel_range,
            repeats_range=repeats_range,
            input_range=input_range,
        )
        matches_res = plot_filter.matches_result(self.plt_cnt_cfg, plot_callback.__name__)
        if matches_res.overall:
            return self.map_plot_panes(
                plot_callback=plot_callback,
                hv_dataset=self.to_hv_dataset(reduce=reduce),
                target_dimension=target_dimension,
                result_var=result_var,
                result_types=result_types,
                **kwargs,
            )
        return matches_res.to_panel()

    def to_panes_multi_panel(
        self,
        hv_dataset: hv.Dataset,
        result_var: ResultVar,
        plot_callback: callable = None,
        target_dimension: int = 1,
        **kwargs,
    ):
        dims = len(hv_dataset.dimensions())
        return self._to_panes_da(
            hv_dataset.data,
            plot_callback=plot_callback,
            target_dimension=target_dimension,
            horizontal=dims <= target_dimension + 1,
            result_var=result_var,
            **kwargs,
        )

    def _to_panes_da(
        self,
        dataset: xr.Dataset,
        plot_callback=pn.pane.panel,
        target_dimension=1,
        horizontal=False,
        result_var=None,
        **kwargs,
    ) -> pn.panel:
        # todo, when dealing with time and repeats, add feature to allow custom order of dimension recursion
        ##todo remove recursion
        num_dims = len(dataset.sizes)
        # print(f"num_dims: {num_dims}, horizontal: {horizontal}, target: {target_dimension}")
        dims = list(d for d in dataset.sizes)

        time_dim_delta = 0
        if self.bench_cfg.over_time:
            time_dim_delta = 0

        if num_dims > (target_dimension + time_dim_delta) and num_dims != 0:
            dim_sel = dims[-1]
            # print(f"selected dim {dim_sel}")

            dim_color = color_tuple_to_css(int_to_col(num_dims - 2, 0.05, 1.0))

            background_col = dim_color
            name = " vs ".join(dims)

            container_args = {"name": name, "styles": {"background": background_col}}
            outer_container = (
                pn.Row(**container_args) if horizontal else pn.Column(**container_args)
            )

            max_len = 0

            for i in range(dataset.sizes[dim_sel]):
                sliced = dataset.isel({dim_sel: i})

                lable_val = sliced.coords[dim_sel].values.item()
                if isinstance(lable_val, (int, float)):
                    lable_val = FormatFloat()(lable_val)

                label = f"{dim_sel}={lable_val}"

                panes = self._to_panes_da(
                    sliced,
                    plot_callback=plot_callback,
                    target_dimension=target_dimension,
                    horizontal=len(sliced.sizes) <= target_dimension + 1,
                    result_var=result_var,
                )
                width = num_dims - target_dimension

                container_args = {
                    "name": name,
                    "styles": {"border-bottom": f"{width}px solid grey"},
                }

                if horizontal:
                    inner_container = pn.Column(**container_args)
                    align = ("center", "center")
                else:
                    inner_container = pn.Row(**container_args)
                    align = ("end", "center")

                label_len = len(label)
                if label_len > max_len:
                    max_len = label_len
                side = pn.pane.Markdown(label, align=align)

                inner_container.append(side)
                inner_container.append(panes)
                outer_container.append(inner_container)
                # outer_container.append(pn.Row(inner_container, align="center"))
            for c in outer_container:
                c[0].width = max_len * 7
        else:
            return plot_callback(dataset=dataset, result_var=result_var, **kwargs)

        return outer_container

    # MAPPING TO LOWER LEVEL BENCHCFG functions so they are available at a top level.
    def to_sweep_summary(self, **kwargs):
        return self.bench_cfg.to_sweep_summary(**kwargs)

    def to_title(self, panel_name: str = None) -> pn.pane.Markdown:
        return self.bench_cfg.to_title(panel_name)

    def to_description(self, width: int = 800) -> pn.pane.Markdown:
        return self.bench_cfg.to_description(width)
