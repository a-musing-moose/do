import os

from contextlib import contextmanager


@contextmanager
def docker_over_ssh(ctx, user, host, key_file=None):
    """
    Creates an SSH connection and forwards the docker socket locally

    Usage:
    ```
        with docker_over_ssh(ctx, "root", "my-host.local") as docker_socket:
            ctx.run(f"docker -H {docker_socket} image ls")
    ```
    """
    key_option = f"-i {key_file}" if key_file else ""
    ctrl_socket = "/tmp/ssh_ctrl.sock"
    docker_socket = "/tmp/remote_docker.sock"

    ctx.run(
        f"ssh -oStrictHostKeyChecking=no  {key_option} -M -S {ctrl_socket} -fnNT "
        f"-L {docker_socket}:/var/run/docker.sock {user}@${host}"
    )
    try:
        yield docker_socket
    finally:
        ctx.run("ssh -S {ctrl_socket} -O exit {user}@{host}")
        if os.path.exists(docker_socket):
            os.unlink(docker_socket)
