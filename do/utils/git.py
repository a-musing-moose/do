from datetime import datetime
from dataclasses import dataclass


@dataclass
class GitInfo:
    short_hash: str
    commit_time: datetime
    current_branch: str


def get_git_info(ctx):
    """
    Returns an `GitInfo` instance based on the latest HEAD
    """
    datetime_string = ctx.run("git log -1 --date=short --pretty=format:%ci").stdout
    commit_time = datetime.strptime(date_string, format="%Y-%m-%d %H:%M:%S %z")
    return GitInfo(
        short_hash=ctx.run("git rev-parse --short HEAD").stdout,
        commit_time=commit_time,
        current_branch=ctx.run("git rev-parse --abbrev-ref HEAD").stdout,
    )
