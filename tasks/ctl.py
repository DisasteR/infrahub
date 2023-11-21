from invoke import Context, task

from .shared import (
    BUILD_NAME,
    NBR_WORKERS,
    build_test_compose_files_cmd,
    build_test_envs,
    execute_command,
    get_env_vars,
)
from .utils import ESCAPED_REPO_PATH, REPO_BASE

MAIN_DIRECTORY = "ctl"
NAMESPACE = "CTL"


# ----------------------------------------------------------------------------
# Documentation
# ----------------------------------------------------------------------------
@task
def generate_doc(context: Context):
    """Generate the documentation for infrahubctl using typer-cli."""
    from infrahub_ctl.cli import app

    print(f" - [{NAMESPACE}] Generate CLI documentation")
    for cmd in app.registered_commands:
        exec_cmd = f'typer --func {cmd.name} infrahub_ctl.cli utils docs --name "infrahubctl {cmd.name}"'
        exec_cmd += f" --output docs/infrahubctl/infrahubctl-{cmd.name}.md"
        with context.cd(ESCAPED_REPO_PATH):
            context.run(exec_cmd)

    for cmd in app.registered_groups:
        exec_cmd = f'typer infrahub_ctl.{cmd.name} utils docs --name "infrahubctl {cmd.name}" --output docs/infrahubctl/infrahubctl-{cmd.name}.md'
        with context.cd(ESCAPED_REPO_PATH):
            context.run(exec_cmd)


# ----------------------------------------------------------------------------
# Formatting tasks
# ----------------------------------------------------------------------------
@task
def format_ruff(context: Context):
    """Run ruff to format all Python files."""

    print(f" - [{NAMESPACE}] Format code with ruff")
    exec_cmd = f"ruff format {MAIN_DIRECTORY} --config {REPO_BASE}/pyproject.toml && "
    exec_cmd += f"ruff check --fix {MAIN_DIRECTORY} --config {REPO_BASE}/pyproject.toml"
    with context.cd(ESCAPED_REPO_PATH):
        context.run(exec_cmd)


@task
def format_autoflake(context: Context):
    """Run autoflack to format all Python files."""

    print(f" - [{NAMESPACE}] Format code with autoflake")
    exec_cmd = f"autoflake --recursive --verbose --in-place --remove-all-unused-imports --remove-unused-variables {MAIN_DIRECTORY}"
    with context.cd(ESCAPED_REPO_PATH):
        context.run(exec_cmd)


@task(name="format")
def format_all(context: Context):
    """This will run all formatter."""

    format_autoflake(context)
    format_ruff(context)

    print(f" - [{NAMESPACE}] All formatters have been executed!")


# ----------------------------------------------------------------------------
# Testing tasks
# ----------------------------------------------------------------------------
@task
def ruff(context: Context, docker: bool = False):
    """Run ruff to check that Python files adherence to standards."""

    print(f" - [{NAMESPACE}] Check code with ruff")
    exec_cmd = f"ruff check --diff {MAIN_DIRECTORY} --config {REPO_BASE}/pyproject.toml"

    if docker:
        compose_files_cmd = build_test_compose_files_cmd(database=False)
        exec_cmd = f"{get_env_vars(context)} docker compose {compose_files_cmd} -p {BUILD_NAME} run {build_test_envs()} infrahub-test {exec_cmd}"
        print(exec_cmd)

    with context.cd(ESCAPED_REPO_PATH):
        context.run(exec_cmd)


@task
def mypy(context: Context, docker: bool = False):
    """This will run mypy for the specified name and Python version."""

    print(f" - [{NAMESPACE}] Check code with mypy")
    exec_cmd = f"mypy --show-error-codes {MAIN_DIRECTORY}"

    if docker:
        compose_files_cmd = build_test_compose_files_cmd(database=False)
        exec_cmd = (
            f"{get_env_vars(context)} docker compose {compose_files_cmd} -p {BUILD_NAME} run infrahub-test {exec_cmd}"
        )
        print(exec_cmd)

    with context.cd(ESCAPED_REPO_PATH):
        context.run(exec_cmd)


@task
def pylint(context: Context, docker: bool = False):
    """This will run pylint for the specified name and Python version."""

    print(f" - [{NAMESPACE}] Check code with pylint")
    exec_cmd = f"pylint {MAIN_DIRECTORY}"

    if docker:
        compose_files_cmd = build_test_compose_files_cmd(database=False)
        exec_cmd = f"{get_env_vars(context)} docker compose {compose_files_cmd} -p {BUILD_NAME} run {build_test_envs()} infrahub-test {exec_cmd}"
        print(exec_cmd)

    with context.cd(ESCAPED_REPO_PATH):
        context.run(exec_cmd)


@task
def lint(context: Context, docker: bool = False):
    """This will run all linter."""
    ruff(context, docker=docker)
    pylint(context, docker=docker)
    mypy(context, docker=docker)

    print(f" - [{NAMESPACE}] All tests have passed!")


@task
def test_unit(context: Context):
    with context.cd(ESCAPED_REPO_PATH):
        compose_files_cmd = build_test_compose_files_cmd(database=False)
        base_cmd = f"{get_env_vars(context)} docker compose {compose_files_cmd} -p {BUILD_NAME} run {build_test_envs()} infrahub-test"
        exec_cmd = f"pytest -n {NBR_WORKERS} -v --cov=infrahub_ctl {MAIN_DIRECTORY}/tests/unit"
        print(f"{base_cmd} {exec_cmd}")
        return execute_command(context=context, command=f"{base_cmd} {exec_cmd}")


@task(default=True)
def format_and_lint(context: Context):
    format_all(context)
    lint(context)
