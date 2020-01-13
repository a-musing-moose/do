from invoke import task
from do.utils import docker_over_ssh


@task()
def hello(c):
    c.run("echo hello, world")
