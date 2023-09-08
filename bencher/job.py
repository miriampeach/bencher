from typing import List, Tuple,Callable
from dataclasses import dataclass, field
from sortedcontainers import SortedDict
from .utils import hash_sha1

from copy import deepcopy
import logging
from diskcache import Cache
from  concurrent.futures import Future, ProcessPoolExecutor

# @dataclass
class Job:
    # id:str
    # kwargs:dict
    # function:Callable
    # result:dict

    def __init__(self,job_id:str,function:Callable,job_args:dict) -> None:
        self.job_id = job_id
        self.function = function
        self.job_args = job_args
        self.job_key = hash_sha1(tuple(SortedDict(self.job_args).items()))   
        # self.cache =None

    # def run_job(self) -> None:
        # self.result = self.function(self.kwargs)

@dataclass 
class JobFuture:
    res:dict 
    def result(self):
        return self.res


def run_job(job:Job,cache:Cache):
    logging.info(f"starting job:{job.job_id}")
    result= job.function(**job.job_args)
    logging.info(f"finished job:{id}")
    cache.set(job.job_key,result)
    return result

class JobCache:

    def __init__(self, parallel:bool=False, cache_name:str="fcache"):       
        self.cache = Cache(f"cachedir/{cache_name}/sample_cache")
        logging.info(f"cache dir{self.cache.directory}")
        if parallel:
            self.executor = ProcessPoolExecutor()
        else:
            self.executor = None
        self.call_count=0


    # def in_cache(self, job:Job)->bool:        
        # if job.job_hash in self.cache:
            # value = self.cache[key]
        # return key, value

    def add_job(self,job:Job,overwrite=False)->JobFuture | Future:       
        if not overwrite and job.job_key in self.cache:
            return JobFuture(self.cache[job.job_key])
        if self.executor is not None:
            return self.executor.submit(run_job, job,self.cache )
        return JobFuture(run_job(job,self.cache))

    def clear_cache(self):
        self.cache.clear()    
    # def clear
    # def call(self,**kwargs)    :
    #     self.add_job(Job(self.call_count))
    #     self.call_count+=1


class JobFunctionCache(JobCache):

    def __init__(self,function:Callable, parallel: bool = False, cache_name: str = "fcache",overwrite=False):
        super().__init__(parallel, cache_name)
        self.function = function
        self.overwrite=overwrite



    def call(self,**kwargs)->JobFuture | Future:
        return self.add_job(Job(self.call_count,self.function,kwargs),overwrite=self.overwrite)



# # #
# # """
# # create list of jobs
# #     for each job
# #             compute
# #             cache result
# #         append future

# #     for future in futures:


# # """


# # def run_cached(function:Callable,**kwargs):
# # results =function(**kwargs)


# def worker_cached(self, bench_cfg, worker_job):
#     function_input_deep = deepcopy(worker_job.function_input)
#     #  function_input_deep = deepcopy(function_input)
#     if not bench_cfg.pass_repeat:
#         function_input_deep.pop("repeat")
#     if "over_time" in function_input_deep:
#         function_input_deep.pop("over_time")
#     if "time_event" in function_input_deep:
#         function_input_deep.pop("time_event")

#     if self.worker_input_cfg is None:  # worker takes kwargs
#         # result = self.worker(worker_job)
#         result = self.worker(**function_input_deep)
#     else:
#         # worker takes a parametrised input object
#         input_cfg = self.worker_input_cfg()
#         for k, v in function_input_deep.items():
#             input_cfg.param.set_param(k, v)

#         result = self.worker(input_cfg)

#     for msg in worker_job.msgs:
#         logging.info(msg)
#     if self.sample_cache is not None and not worker_job.found_in_cache:
#         self.sample_cache.set(
#             worker_job.function_input_signature_benchmark_context, result, tag=worker_job.tag
#         )
#         self.sample_cache.set(worker_job.function_input_signature_pure, result, tag=worker_job.tag)
#     return result


# @dataclass
# class WorkerJob:
#     function_input_vars: List
#     index_tuple: Tuple[int]
#     dims_name: List[str]
#     constant_inputs: dict
#     bench_cfg_sample_hash: str
#     tag: str

#     function_input: SortedDict = None
#     fn_inputs_sorted: List[str] = None
#     function_input_signature_pure: str = None
#     function_input_signature_benchmark_context: str = None
#     found_in_cache: bool = False
#     msgs: List[str] = field(default_factory=list)

#     def setup_hashes(self) -> None:
#         self.function_input = SortedDict(zip(self.dims_name, self.function_input_vars))

#         if self.constant_inputs is not None:
#             self.function_input = self.function_input | self.constant_inputs

#         # store a tuple of the inputs as keys for a holomap
#         # the signature is the hash of the inputs to to the function + meta variables such as repeat and time + the hash of the benchmark sweep as a whole (without the repeats hash)
#         self.fn_inputs_sorted = list(SortedDict(self.function_input).items())
#         self.function_input_signature_pure = hash_sha1((self.fn_inputs_sorted, self.tag))

#         self.function_input_signature_benchmark_context = hash_sha1(
#             (self.function_input_signature_pure, self.bench_cfg_sample_hash)
#         )

#     # def call_worker(self,):
