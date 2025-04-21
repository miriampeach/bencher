"""This file demonstrates benchmarking with 3 categorical inputs and 2 output variables.

It benchmarks different Python operations to compare their performance characteristics.
"""

import random
import time
import sys
import bencher as bch

random.seed(0)


class PythonOperationsBenchmark(bch.ParametrizedSweep):
    """Example class for benchmarking different Python operations using categorical variables."""

    data_structure = bch.StringSweep(
        ["list", "dict"], doc="Type of data structure to operate on"
    )
    operation_type = bch.StringSweep(
        ["read", "write"], doc="Type of operation to perform"
    )
    data_size = bch.StringSweep(
        ["small", "medium"], doc="Size of data to process"
    )

    execution_time = bch.ResultVar(units="ms", doc="Execution time in milliseconds")
    memory_usage = bch.ResultVar(units="bytes", doc="Actual memory usage in bytes")

    def __call__(self, **kwargs) -> dict:
        """Execute the benchmark for the given set of parameters.

        Args:
            **kwargs: Parameters to update before executing

        Returns:
            dict: Dictionary containing the benchmark results
        """
        self.update_params_from_kwargs(**kwargs)

        # Determine data size
        if self.data_size == "small":
            size = 1000
        else:  # medium
            size = 10000

        # Create test data according to the specified data structure
        if self.data_structure == "list":
            if self.operation_type == "read":
                # Benchmark list access operations
                data = list(range(size))
                start_time = time.perf_counter()
                
                # Perform random access operations
                for _ in range(1000):
                    _ = data[random.randint(0, size-1)]
                
                end_time = time.perf_counter()
                self.execution_time = (end_time - start_time) * 1000  # Convert to ms
                self.memory_usage = sys.getsizeof(data)
                
                # Measure memory of individual elements to get a more accurate picture
                sample_size = min(100, size)
                for i in random.sample(range(size), sample_size):
                    self.memory_usage += sys.getsizeof(data[i])
                # Scale up to estimate total including overhead
                self.memory_usage = int(self.memory_usage * (size / sample_size))
            
            else:  # write
                # Benchmark list append operations
                data = []
                start_time = time.perf_counter()
                
                # Perform append operations
                for i in range(size):
                    data.append(i)
                
                end_time = time.perf_counter()
                self.execution_time = (end_time - start_time) * 1000  # Convert to ms
                
                # Measure actual memory usage
                self.memory_usage = sys.getsizeof(data)
                
                # Add memory of individual elements
                sample_size = min(100, size)
                for i in random.sample(range(size), sample_size):
                    self.memory_usage += sys.getsizeof(data[i])
                # Scale up to estimate total including overhead
                self.memory_usage = int(self.memory_usage * (size / sample_size))
        
        else:  # dict
            if self.operation_type == "read":
                # Benchmark dictionary access operations
                data = {i: i for i in range(size)}
                start_time = time.perf_counter()
                
                # Perform random access operations
                for _ in range(1000):
                    _ = data[random.randint(0, size-1)]
                
                end_time = time.perf_counter()
                self.execution_time = (end_time - start_time) * 1000  # Convert to ms
                
                # Measure actual memory usage
                self.memory_usage = sys.getsizeof(data)
                
                # Add memory of a sample of keys and values
                sample_size = min(100, size)
                sample_keys = random.sample(list(data.keys()), sample_size)
                for k in sample_keys:
                    self.memory_usage += sys.getsizeof(k) + sys.getsizeof(data[k])
                # Scale up to estimate total including overhead
                self.memory_usage = int(self.memory_usage * (size / sample_size))
            
            else:  # write
                # Benchmark dictionary insertion operations
                data = {}
                start_time = time.perf_counter()
                
                # Perform insertion operations
                for i in range(size):
                    data[i] = i
                
                end_time = time.perf_counter()
                self.execution_time = (end_time - start_time) * 1000  # Convert to ms
                
                # Measure actual memory usage
                self.memory_usage = sys.getsizeof(data)
                
                # Add memory of a sample of keys and values
                sample_size = min(100, size)
                sample_keys = random.sample(list(data.keys()), sample_size)
                for k in sample_keys:
                    self.memory_usage += sys.getsizeof(k) + sys.getsizeof(data[k])
                # Scale up to estimate total including overhead
                self.memory_usage = int(self.memory_usage * (size / sample_size))

        # Add a little variability to make the benchmark more realistic
        self.execution_time *= random.uniform(0.95, 1.05)
        
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
        description="Comparing execution time and memory usage across Python data structures and operations"
    )
    return bench


if __name__ == "__main__":
    example_3_cat_in_2_out().report.show()
