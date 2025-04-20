"""This file demonstrates benchmarking with 3 categorical inputs and 2 output variables."""

import random
import bencher as bch

random.seed(0)


class Example3Cat2Out(bch.ParametrizedSweep):
    """Example class for 3 categorical parameter sweep with two output variables."""

    product_type = bch.StringSweep(["electronics", "clothing", "home"], doc="Type of product")
    price_range = bch.StringSweep(["budget", "mid-range", "premium"], doc="Price range of product")
    target_audience = bch.StringSweep(
        ["youth", "adult", "senior"], doc="Target audience for product"
    )

    expected_sales = bch.ResultVar(units="units", doc="Expected sales volume")
    customer_satisfaction = bch.ResultVar(units="score", doc="Customer satisfaction score (1-100)")

    def __call__(self, **kwargs) -> dict:
        """Execute the parameter sweep for the given inputs.

        Args:
            **kwargs: Additional parameters to update before executing

        Returns:
            dict: Dictionary containing the outputs of the parameter sweep
        """
        self.update_params_from_kwargs(**kwargs)

        # Base sales and satisfaction values based on product type
        if self.product_type == "electronics":
            base_sales = 1000
            base_satisfaction = 75
        elif self.product_type == "clothing":
            base_sales = 1500
            base_satisfaction = 70
        else:  # home
            base_sales = 800
            base_satisfaction = 80

        # Modify based on price range
        if self.price_range == "budget":
            sales_modifier = 1.5
            satisfaction_modifier = 0.9
        elif self.price_range == "mid-range":
            sales_modifier = 1.2
            satisfaction_modifier = 1.1
        else:  # premium
            sales_modifier = 0.8
            satisfaction_modifier = 1.3

        # Modify based on target audience
        if self.target_audience == "youth":
            if self.product_type == "electronics":
                audience_sales_modifier = 1.4
                audience_satisfaction_modifier = 1.1
            elif self.product_type == "clothing":
                audience_sales_modifier = 1.3
                audience_satisfaction_modifier = 1.2
            else:  # home
                audience_sales_modifier = 0.7
                audience_satisfaction_modifier = 0.8
        elif self.target_audience == "adult":
            audience_sales_modifier = 1.2
            audience_satisfaction_modifier = 1.0
        else:  # senior
            if self.product_type == "electronics":
                audience_sales_modifier = 0.6
                audience_satisfaction_modifier = 0.7
            elif self.product_type == "clothing":
                audience_sales_modifier = 0.8
                audience_satisfaction_modifier = 0.9
            else:  # home
                audience_sales_modifier = 1.3
                audience_satisfaction_modifier = 1.2

        # Calculate final values with some randomness
        self.expected_sales = int(
            base_sales * sales_modifier * audience_sales_modifier * random.uniform(0.9, 1.1)
        )
        self.customer_satisfaction = min(
            100,
            base_satisfaction
            * satisfaction_modifier
            * audience_satisfaction_modifier
            * random.uniform(0.95, 1.05),
        )

        return super().__call__(**kwargs)


def example_3_cat_in_2_out(
    run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None
) -> bch.Bench:
    """This example shows how to create a benchmark with 3 categorical input variables
    and 2 output variables.

    Args:
        run_cfg: Configuration for the benchmark run
        report: Report to append the results to

    Returns:
        bch.Bench: The benchmark object
    """

    if run_cfg is None:
        run_cfg = bch.BenchRunCfg()
    run_cfg.repeats = 10
    bench = Example3Cat2Out().to_bench(run_cfg, report)
    bench.plot_sweep()
    return bench


if __name__ == "__main__":
    example_3_cat_in_2_out().report.show()
