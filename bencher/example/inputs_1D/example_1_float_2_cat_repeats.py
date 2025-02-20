import bencher as bch
from bencher.example.meta.example_meta import BenchableObject

run_cfg = bch.BenchRunCfg()
run_cfg.repeats = 20
run_cfg.level = 4
bench = BenchableObject().to_bench(run_cfg)
res = bench.plot_sweep(
    input_vars=["float1", "noisy", "noise_distribution"], result_vars=["distance", "sample_noise"]
)

bench.report.show()