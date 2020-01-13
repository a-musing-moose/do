from invoke import task
from do.utils import docker_over_ssh  # noqa: F401


@task()
def hello(c):
    c.run("echo hello, world")
