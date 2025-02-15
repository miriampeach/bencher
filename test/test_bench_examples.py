import unittest
import bencher as bch
from bencher.example.example_floats2D import example_floats2D
from bencher.example.example_pareto import example_pareto
from bencher.example.example_simple_cat import example_1D_cat
from bencher.example.example_simple_float import example_1D_float
from bencher.example.example_float_cat import run_example_float_cat
from bencher.example.example_time_event import run_example_time_event
from bencher.example.example_float3D import example_floats3D

from bencher.example.example_custom_sweep import example_custom_sweep
from bencher.example.example_workflow import example_floats2D_workflow, example_floats3D_workflow
from bencher.example.example_holosweep import example_holosweep
from bencher.example.example_holosweep_tap import example_holosweep_tap

from bencher.example.optuna.example_optuna import optuna_rastrigin
from bencher.example.example_sample_cache import example_sample_cache
from bencher.example.example_strings import example_strings
from bencher.example.example_image import example_image
from bencher.example.example_video import example_video
from bencher.example.meta.example_meta import example_meta
from bencher.example.example_docs import example_docs

import os

# shelved
# from bencher.example.shelved.example_float2D_scatter import example_floats2D_scatter
# from bencher.example.shelved.example_float3D_cone import example_cone


class TestBenchExamples(unittest.TestCase):
    """The purpose of this test class is to run the example problems to make sure they don't crash.  The bencher logic is tested in the other test files test_bencher.py and test_vars.py"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.generate_all = False

    def create_run_cfg(self) -> bch.BenchRunCfg:
        cfg = bch.BenchRunCfg()
        if not self.generate_all:
            cfg.repeats = 2  # low number of repeats to reduce test time, but also test averaging and variance code
            cfg.debug = True  # reduce size of param sweep so tests are faster
        cfg.clear_cache = True
        return cfg

    def examples_asserts(self, example_result, save=False) -> None:
        self.assertIsNotNone(example_result)
        if save or self.generate_all:
            path = example_result.report.save_index("cachedir")
            self.assertTrue(os.path.exists(path))

    def test_publish_docs(self):
        report = example_docs(run_cfg=self.create_run_cfg())
        report.save_index()

    # def test_example_categorical(self) -> None:
    #     self.examples_asserts(example_categorical(self.create_run_cfg()))

    # def test_example_floats(self) -> None:
    #     self.examples_asserts(example_floats(self.create_run_cfg()))

    def test_example_simple_cat(self) -> None:
        self.examples_asserts(example_1D_cat(self.create_run_cfg()))

    def test_example_floats2D(self) -> None:
        self.examples_asserts(example_floats2D(self.create_run_cfg()))

    def test_example_pareto(self) -> None:
        self.examples_asserts(example_pareto(self.create_run_cfg()))

    def test_example_simple_float(self) -> None:
        self.examples_asserts(example_1D_float(self.create_run_cfg()))

    def test_example_float_cat(self) -> None:
        self.examples_asserts(run_example_float_cat(self.create_run_cfg()))

    def test_example_time_event(self) -> None:
        self.examples_asserts(run_example_time_event(self.create_run_cfg()))

    def test_example_float3D(self) -> None:
        self.examples_asserts(example_floats3D(self.create_run_cfg()))

    def test_example_custom_sweep(self) -> None:
        self.examples_asserts(example_custom_sweep(self.create_run_cfg()))

    def test_example_floats2D_workflow(self) -> None:
        self.examples_asserts(example_floats2D_workflow(self.create_run_cfg()))

    def test_example_floats3D_workflow(self) -> None:
        self.examples_asserts(example_floats3D_workflow(self.create_run_cfg()))

    def test_holosweep(self) -> None:
        self.examples_asserts(example_holosweep(self.create_run_cfg()))

    def test_holosweep_tap(self) -> None:
        self.examples_asserts(example_holosweep_tap(self.create_run_cfg()))

    def test_optuna_rastrigin(self) -> None:
        self.examples_asserts(optuna_rastrigin(self.create_run_cfg()))

    def test_example_sample_cache(self) -> None:
        self.examples_asserts(example_sample_cache(self.create_run_cfg(), trigger_crash=False))

    def test_example_strings(self) -> None:
        self.examples_asserts(example_strings(self.create_run_cfg()))

    def test_example_image(self) -> None:
        self.examples_asserts(example_image(self.create_run_cfg()))

    def test_example_video(self) -> None:
        self.examples_asserts(example_video(self.create_run_cfg()))

    def test_example_meta(self) -> None:
        self.examples_asserts(example_meta(self.create_run_cfg()))

    # def test_example_meta_scatter(self) -> None:
    # self.examples_asserts(example_meta_scatter(self.create_run_cfg()))

    # shelved
    # def test_example_cone(self) -> None:
    #     self.examples_asserts(example_cone(self.create_run_cfg()))
    # def test_float2D_scatter(self) -> None:
    #     self.examples_asserts(example_floats2D_scatter(self.create_run_cfg()))
