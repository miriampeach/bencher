"""This file demonstrates benchmarking with 3 categorical inputs and 2 output variables.

It benchmarks different Python operations to compare their performance characteristics.
"""

import random
import time
import tracemalloc
import bencher as bch

random.seed(0)


class PythonOperationsBenchmark(bch.ParametrizedSweep):
    """Example class for benchmarking different Python operations using categorical variables."""

    data_structure = bch.StringSweep(["list", "dict"], doc="Type of data structure to operate on")
    operation_type = bch.StringSweep(["read", "write"], doc="Type of operation to perform")
    data_size = bch.StringSweep(["small", "medium"], doc="Size of data to process")

    execution_time = bch.ResultVar(units="ms", doc="Execution time in milliseconds")
    memory_peak = bch.ResultVar(units="KB", doc="Peak memory usage in kilobytes")

    def _run_benchmark(self, operation_func):
        """Run a benchmark operation with memory tracing and timing.

        Args:
            operation_func: Function to benchmark

        Returns:
            tuple: (execution_time_ms, peak_memory_kb)
        """
        # Start tracing memory allocations
        tracemalloc.start()
        tracemalloc.clear_traces()

        # Perform timed operation
        start_time = time.perf_counter()
        operation_func()
        end_time = time.perf_counter()

        # Get memory usage and stop tracing
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Calculate metrics with some natural variation
        execution_time_ms = (end_time - start_time) * 1000  # Convert to ms
        peak_memory_kb = peak / 1024  # Convert bytes to KB

        return execution_time_ms, peak_memory_kb

    def __call__(self, **kwargs) -> dict:
        """Execute the benchmark for the given set of parameters.

        Args:
            **kwargs: Parameters to update before executing

        Returns:
            dict: Dictionary containing the benchmark results
        """
        self.update_params_from_kwargs(**kwargs)

        # Determine data size
        size = 100 if self.data_size == "small" else 1000

        # Define operations based on parameters
        if self.data_structure == "list":
            data = list(range(size)) if self.operation_type == "read" else []
            if self.operation_type == "read":

                def operation():
                    return [data[random.randint(0, size - 1)] for _ in range(size)]
            else:  # write

                def operation():
                    return [data.append(i) for i in range(size)]
        else:  # dict
            data = {i: i for i in range(size)} if self.operation_type == "read" else {}
            if self.operation_type == "read":

                def operation():
                    return [data[random.randint(0, size - 1)] for _ in range(size)]
            else:  # write

                def operation():
                    return [data.update({i: i}) for i in range(size)]

        # Run the benchmark
        self.execution_time, self.memory_peak = self._run_benchmark(operation)

        return super().__call__(**kwargs)


def example_3_cat_in_2_out(
    run_cfg: bch.BenchRunCfg = None, report: bch.BenchReport = None
) -> bch.Bench:
    """This example benchmarks common Python operations with different data structures,
    operation types, and data sizes.

    Args:
        run_cfg: Configuration for the benchmark run
        report: Report to append the results to

    Returns:
        bch.Bench: The benchmark object
    """

    if run_cfg is None:
        run_cfg = bch.BenchRunCfg()
    run_cfg.repeats = 5  # Fewer repeats for a quicker benchmark
    bench = PythonOperationsBenchmark().to_bench(run_cfg, report)
    bench.plot_sweep(
        title="Python Operations Performance Benchmark",
        description="Comparing execution time and peak memory usage across Python data structures and operations",
    )
    return bench


if __name__ == "__main__":
    example_3_cat_in_2_out().report.show()
