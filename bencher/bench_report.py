import logging
from typing import Callable
import os
import panel as pn
from pathlib import Path
import shutil
from threading import Thread

from bencher.results.bench_result import BenchResult
from bencher.bench_plot_server import BenchPlotServer
from bencher.bench_cfg import BenchRunCfg


class BenchReport(BenchPlotServer):
    def __init__(
        self,
        bench_name: str = None,
    ) -> None:
        self.bench_name = bench_name
        self.pane = pn.Tabs(tabs_location="left", name=self.bench_name)

    def append_title(self, title: str, new_tab: bool = True):
        if new_tab:
            return self.append_tab(pn.pane.Markdown(f"# {title}", name=title), title)
        return self.append_markdown(f"# {title}", title)

    def append_markdown(self, markdown: str, name=None, width=800, **kwargs) -> pn.pane.Markdown:
        if name is None:
            name = markdown
        md = pn.pane.Markdown(markdown, name=name, width=width, **kwargs)
        self.append(md, name)
        return md

    def append(self, pane: pn.panel, name: str = None) -> None:
        if len(self.pane) == 0:
            if name is None:
                name = pane.name
            self.append_tab(pane, name)
        else:
            self.pane[-1].append(pane)

    def append_col(self, pane: pn.panel, name: str = None) -> None:
        if name is not None:
            col = pn.Column(pane, name=name)
        else:
            col = pn.Column(pane, name=pane.name)
        self.pane.append(col)

    def append_result(self, bench_res: BenchResult) -> None:
        self.append_tab(bench_res.to_auto_plots(), bench_res.bench_cfg.title)

    def append_tab(self, pane: pn.panel, name: str = None) -> None:
        if pane is not None:
            if name is None:
                name = pane.name
            self.pane.append(pn.Column(pane, name=name))

    def save_index(self, directory="", filename="index.html") -> Path:
        """Saves the result to index.html in the root folder so that it can be displayed by github pages.

        Returns:
            Path: save path
        """
        return self.save(directory, filename, False)

    def save(
        self,
        directory: str | Path = "cachedir",
        filename: str = None,
        in_html_folder: bool = True,
        **kwargs,
    ) -> Path:
        """Save the result to a html file.  Note that dynamic content will not work.  by passing save(__file__) the html output will be saved in the same folder as the source code in a html subfolder.

        Args:
            directory (str | Path, optional): base folder to save to. Defaults to "cachedir" which should be ignored by git.
            filename (str, optional): The name of the html file. Defaults to the name of the benchmark
            in_html_folder (bool, optional): Put the saved files in a html subfolder to help keep the results separate from source code. Defaults to True.

        Returns:
            Path: the save path
        """

        if filename is None:
            filename = f"{self.bench_name}.html"

        base_path = Path(directory)

        if in_html_folder:
            base_path /= "html"

        logging.info(f"creating dir {base_path.absolute()}")
        os.makedirs(base_path.absolute(), exist_ok=True)

        base_path = base_path / filename

        logging.info(f"saving html output to: {base_path.absolute()}")

        self.pane.save(filename=base_path, progress=True, embed=True, **kwargs)
        return base_path

    def show(self, run_cfg: BenchRunCfg = None) -> Thread:  # pragma: no cover
        """Launches a webserver with plots of the benchmark results, blocking

        Args:
            run_cfg (BenchRunCfg, optional): Options for the webserve such as the port. Defaults to None.

        """
        if run_cfg is None:
            run_cfg = BenchRunCfg()

        return BenchPlotServer().plot_server(self.bench_name, run_cfg, self.pane)

    def publish(
        self, remote_callback: Callable, branch_name: str = None, debug: bool = False
    ) -> str:  # pragma: no cover
        """Publish the results as an html file by committing it to the bench_results branch in the current repo. If you have set up your repo with github pages or equivalent then the html file will be served as a viewable webpage.  This is an example of a callable to publish on github pages:

        .. code-block:: python

            def publish_args(branch_name) -> Tuple[str, str]:
                return (
                    "https://github.com/dyson-ai/bencher.git",
                    f"https://github.com/dyson-ai/bencher/blob/{branch_name}")


        Args:
            remote (Callable): A function the returns a tuple of the publishing urls. It must follow the signature def publish_args(branch_name) -> Tuple[str, str].  The first url is the git repo name, the second url needs to match the format for viewable html pages on your git provider.  The second url can use the argument branch_name to point to the report on a specified branch.

        Returns:
            str: the url of the published report
        """

        if branch_name is None:
            branch_name = self.bench_name
        branch_name += "_debug" if debug else ""

        remote, publish_url = remote_callback(branch_name)

        directory = "tmpgit"
        report_path = self.save(directory, filename="index.html", in_html_folder=False)
        logging.info(f"created report at: {report_path.absolute()}")

        cd_dir = f"cd {directory} &&"

        os.system(f"{cd_dir} git init")
        os.system(f"{cd_dir} git checkout -b {branch_name}")
        os.system(f"{cd_dir} git add index.html")
        os.system(f'{cd_dir} git commit -m "publish {branch_name}"')
        os.system(f"{cd_dir} git remote add origin {remote}")
        os.system(f"{cd_dir} git push --set-upstream origin {branch_name} -f")

        logging.info("Published report @")
        logging.info(publish_url)

        shutil.rmtree(directory)

        return publish_url


# def append(self,pane):
# self.report.append(pane)

# def __getstate__(self):
#     state = self.__dict__.copy()
#     # Don't pickle baz
#     del state["pane"]
#     return state

# def __setstate__(self, state):
#     self.__dict__.update(state)
#     # Add baz back since it doesn't exist in the pickle
#     self.report = []

# def publish_old(
#     self,
#     directory: str = "bench_results",
#     branch_name: str = "bench_results",
#     url_postprocess: Callable = None,
#     **kwargs,
# ) -> str:
#     """Publish the results as an html file by committing it to the bench_results branch in the current repo. If you have set up your repo with github pages or equivalent then the html file will be served as a viewable webpage.

#     Args:
#         directory (str, optional): Directory to save the results. Defaults to "bench_results".
#         branch_name (str, optional): Branch to publish on. Defaults to "bench_results".
#         url_postprocess (Callable, optional): A function that maps the origin url to a github pages url. Pass your own function if you are using another git providers. Defaults to None.

#     Returns:
#         str: _description_
#     """

#     def get_output(cmd: str) -> str:
#         return (
#             subprocess.run(cmd.split(" "), stdout=subprocess.PIPE, check=False)
#             .stdout.decode("utf=8")
#             .strip()
#         )

#     def postprocess_url(publish_url: str, branch_name: str, report_path: str, **kwargs) -> str:
#         # import re

#         # return re.sub(
#         #     """((git|ssh|http(s)?)|(git@[\w\.-]+))(:(//)?)([\w\.@\:/\-~]+)(\.git)(/)?""",
#         #     """https://$7/""",
#         #     publish_url,
#         # )
#         # git@github.com:user/project.git
#         # https://github.com/user/project.git
#         # http://github.com/user/project.git
#         # git@192.168.101.127:user/project.git
#         # https://192.168.101.127/user/project.git
#         # http://192.168.101.127/user/project.git
#         # ssh://user@host.xz:port/path/to/repo.git/
#         # ssh://user@host.xz/path/to/repo.git/
#         # ssh://host.xz:port/path/to/repo.git/
#         # ssh://host.xz/path/to/repo.git/
#         # ssh://user@host.xz/path/to/repo.git/
#         # ssh://host.xz/path/to/repo.git/
#         # ssh://user@host.xz/~user/path/to/repo.git/
#         # ssh://host.xz/~user/path/to/repo.git/
#         # ssh://user@host.xz/~/path/to/repo.git
#         # ssh://host.xz/~/path/to/repo.git
#         # git://host.xz/path/to/repo.git/
#         # git://host.xz/~user/path/to/repo.git/
#         # http://host.xz/path/to/repo.git/
#         # https://host.xz/path/to/repo.git/
#         # https://regex101.com/r/qT7NP0/3

#         return publish_url.replace(".git", f"/blob/{directory}/{report_path}")

#     if url_postprocess is None:
#         url_postprocess = postprocess_url
#     current_branch = get_output("git symbolic-ref --short HEAD")
#     logging.info(f"on branch: {current_branch}")
#     stash_msg = get_output("git stash")
#     logging.info(f"stashing current work :{stash_msg}")
#     checkout_msg = get_output(f"git checkout -b {branch_name}")
#     checkout_msg = get_output(f"git checkout {branch_name}")
#     get_output("git pull")

#     logging.info(f"checking out branch: {checkout_msg}")
#     report_path = self.save(directory, in_html_folder=False)
#     logging.info(f"created report at: {report_path.absolute()}")
#     # commit_msg = f""
#     logging.info("adding report to git")
#     get_output(f"git add {report_path.absolute()}")
#     get_output("git status")
#     logging.info("committing report")
#     cmd = f'git commit -m "generate_report:{self.bench_name}"'
#     logging.info(cmd)
#     get_output(cmd)
#     logging.info("pushing report to origin")
#     get_output(f"git push --set-upstream origin {branch_name}")
#     logging.info("checking out original branch")
#     get_output(f"git checkout {current_branch}")
#     if "No local changes" not in stash_msg:
#         logging.info("restoring work with git stash pop")
#         get_output("git stash pop")

#     publish_url = get_output("git remote get-url --push origin")
#     logging.info(f"raw url:{publish_url}")
#     publish_url = url_postprocess(
#         publish_url, branch_name=branch_name, report_path=report_path, **kwargs
#     )
#     logging.info("Published report @")
#     logging.info(publish_url)
#     return publish_url
