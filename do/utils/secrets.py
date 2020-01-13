import os
import re
import sys
import shlex
from shutil import which
from contextlib import contextmanager
from hashlib import md5
from pathlib import Path

from invoke import task


from .paths import PROJECT_PATH, PROJECT_SLUG


PASSPHRASE_PATH = Path.home() / ".passphrases" / f"{PROJECT_SLUG}.passphrase"


def _get_secret_path(name):
    return PROJECT_PATH / "environments" / f"{name}.env.gpg"


def _get_env_path(name):
    return PROJECT_PATH / "environments" / f"{name}.env"


def _encrypt(ctx, name):
    # secret_path = _get_secret_path(name)
    env_path = _get_env_path(name)

    result = ctx.run(
        f"gpg --passphrase-file {PASSPHRASE_PATH} --symmetric --yes --batch {env_path}"
    )
    if result.exited == 0:
        env_path.unlink()
    else:
        print(
            f"Error encrypting {env_path}, the file has been left unencrypted",
            file=sys.stderr,
        )


def _decrypt(ctx, name, create=False):
    secret_path = _get_secret_path(name)
    env_path = _get_env_path(name)

    if not secret_path.exists():
        secret_path.parent.mkdir(parents=True, exist_ok=True)
        secret_path.touch()
        _encrypt(ctx, name)

    ctx.run(
        f"gpg --passphrase-file {PASSPHRASE_PATH} --yes "
        f"--batch -d -o {env_path} {secret_path}"
    )


def _apply_secrets(name):
    content = _get_env_path(name).read_text(encoding="utf-8")
    for line in content.splitlines():
        tokens = list(shlex.shlex(line, posix=True))
        # parses the assignment statement
        if len(tokens) < 3:
            continue
        name, op = tokens[:2]
        value = "".join(tokens[2:])
        if op != "=":
            continue
        if not re.match(r"[A-Za-z_][A-Za-z_0-9]*", name):
            continue
        value = value.replace(r"\n", "\n").replace(r"\t", "\t")
        os.environ.setdefault(name, value)


@contextmanager
def environment(ctx, name):
    """
    A context processor that decrypts the named secrets file, along with the common secrets
    and exports them to the current environment

    Usage:
    ```
    with environment(ctx, "local"):
        ctx.run("yarn build")
    ```
    """
    original_env = os.environ.copy()
    try:
        _decrypt(ctx, "common", create=True)
        _apply_secrets("common")
        _encrypt(ctx, "common")

        _decrypt(ctx, name, create=True)
        _apply_secrets(name)
        _encrypt(ctx, name)
        yield os.environ
    finally:
        os.environ.clear()
        os.environ.update(original_env)


@task()
def edit_secrets(ctx, name):
    """
    Decrypts and opens for editing the environments file for the named environment. 'common' is used for
    shared secrets
    """
    editor = None
    candidates = filter(
        lambda x: x is not None,
        [os.environ.get("EDITOR", None), "nano", "vim", "vi", "emacs"],
    )
    for candidate in candidates:
        if which(candidate):
            editor = candidate
            break
    if not editor:
        print(
            f"No editors found, tried {candidates}, please ensure `EDITOR` is set to your preferred editor",
            file=sys.stderr,
        )
        sys.exit(1)

    env_path = _get_env_path(name)
    checksum = md5(env_path.read_bytes()).digest()
    ctx.run(f"{editor} {env_path}", pty=True)
    if checksum != md5(env_path.read_bytes()).digest():
        print("Changes detected, re-encrypting")
        _encrypt(ctx, name)
    else:
        print("No changes detected")
