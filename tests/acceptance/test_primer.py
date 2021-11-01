# Licensed under the GPL: https://www.gnu.org/licenses/old-licenses/gpl-2.0.html
# For details: https://github.com/PyCQA/pylint/blob/main/LICENSE

import contextlib
import os
import subprocess
import sys

import pytest
from git import Repo

PRIMER_DIRECTORY = ".pylint_primer_tests"


@contextlib.contextmanager
def _patch_stdout(out):
    sys.stdout = out
    try:
        yield
    finally:
        sys.stdout = sys.__stdout__


def lazy_git_clone(git_url: str, target_directory: str) -> None:
    if not os.path.exists(target_directory):
        Repo.clone_from(git_url, target_directory)


@pytest.mark.acceptance
@pytest.mark.parametrize(
    "git_url,directories_to_lint",
    [
        ["https://github.com/psf/black.git", "src tests"],
        ["https://github.com/numpy/numpy.git", "numpy"],
    ],
)
def test_primer(git_url, directories_to_lint):
    parts = git_url.split("/")  # ["https:", "github.com", "psf" "black.git"]
    namespace = parts[-2]  # "psf"
    project = parts[-1][:-4]  # "black", :-4 removes ".git"
    target_directory = f"{PRIMER_DIRECTORY}/{namespace}/{project}"
    lazy_git_clone(git_url, target_directory)
    os.chdir(target_directory)
    try:
        # We only check for crash and errors as warning are not stable
        # We suppose that errors in a big lib come from a pylint false positive
        subprocess.run(
            ["pylint"] + directories_to_lint.split(" ") + ["--errors-only"],
            check=True,
        )
    except SystemExit as ex:
        assert ex.code == 0
        return
