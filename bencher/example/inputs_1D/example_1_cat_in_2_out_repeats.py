import random
import bencher as bch

random.seed(0)

class ExampleCat1D(bch.ParametrizedSweep):
    population = bch.StringSweep(["population1", "population2"], doc="Distribution to sample from")
    age= bch.ResultVar(units="v", doc="sin of theta")
    children= bch.ResultVar(units="v", doc="sin of theta")

    def __call__(self, **kwargs):
        self.update_params_from_kwargs(**kwargs)

        if self.population == "population1":
            self.age= random.gauss(mu=50.0,sigma=10.0)
            self.children= random.gauss(mu=1.5)
        else:
            self.age= random.gauss(mu=60,sigma=20)
            self.children= random.gauss(mu=3.)

        return super().__call__(**kwargs)


def example_1_cat_in_2_out_repeats(
    run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None
) -> bch.Bench:
    """This example shows how to sample a 1 dimensional float variable and plot the result of passing that parameter sweep to the benchmarking function"""

    if run_cfg is None:
        run_cfg = bch.BenchRunCfg()
    run_cfg.repeats = 20
    bench = ExampleCat1D().to_bench(run_cfg, report)
    bench.plot_sweep()
    return bench


if __name__ == "__main__":
    example_1_cat_in_2_out_repeats().report.show()
