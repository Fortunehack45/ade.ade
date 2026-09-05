"""Automated tests for Ade CLI commands."""

import io
from contextlib import redirect_stdout, redirect_stderr
from ade.cli.main import main
from ade import __version__


def test_cli_version():
    out = io.StringIO()
    with redirect_stdout(out):
        ret = main(["--version"])
    assert ret == 0
    assert f"Ade {__version__}" in out.getvalue()


def test_cli_help():
    out = io.StringIO()
    with redirect_stdout(out):
        ret = main(["--help"])
    assert ret == 0
    assert "Usage:" in out.getvalue()
    assert "ade run" in out.getvalue()


def test_cli_run_hello():
    out = io.StringIO()
    with redirect_stdout(out):
        ret = main(["run", "examples/hello.ade"])
    assert ret == 0
    assert "Hello, World!" in out.getvalue()


def test_cli_run_milestone():
    out = io.StringIO()
    with redirect_stdout(out):
        ret = main(["run", "examples/milestone_program.ade"])
    assert ret == 0
    lines = out.getvalue().strip().splitlines()
    assert lines == ["Hello, Fortune", "15"]


def test_cli_future_command():
    err = io.StringIO()
    with redirect_stderr(err):
        ret = main(["build", "main.ade"])
    assert ret == 1
    assert "scheduled for Phase 11" in err.getvalue()
