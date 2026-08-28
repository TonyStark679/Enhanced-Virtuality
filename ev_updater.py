#!/usr/bin/env python3

"""
E.V. Self Updater
Enhanced Virtuality

Safely checks the Git repository for updates and can update the
local installation without overwriting uncommitted changes.

Designed for Termux, Linux, and Windows.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


# ============================================================
# E.V. CONFIGURATION
# ============================================================

APP_NAME = "E.V."
APP_FULL_NAME = "Enhanced Virtuality"

PROJECT_DIR = Path(
    os.getenv(
        "JARVIS_PROJECT_DIR",
        str(Path(__file__).resolve().parent),
    )
).expanduser().resolve()

DEFAULT_BRANCH = os.getenv(
    "JARVIS_BRANCH",
    "",
).strip()

AUTO_UPDATE = os.getenv(
    "JARVIS_AUTO_UPDATE",
    "false",
).strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

CHECK_TIMEOUT = int(
    os.getenv(
        "JARVIS_UPDATE_TIMEOUT",
        "30",
    )
)

MAIN_SCRIPT = os.getenv(
    "JARVIS_MAIN_SCRIPT",
    "jarvis.py",
).strip()


# ============================================================
# ANSI
# ============================================================

ANSI = {
    "reset": "\033[0m",
    "dim": "\033[2m",
    "cyan": "\033[38;5;117m",
    "blue": "\033[38;5;111m",
    "purple": "\033[38;5;141m",
    "magenta": "\033[38;5;207m",
    "green": "\033[38;5;114m",
    "yellow": "\033[38;5;221m",
    "red": "\033[38;5;203m",
    "white": "\033[38;5;255m",
}


def color(
    text: str,
    name: str,
) -> str:
    return (
        f"{ANSI.get(name, '')}"
        f"{text}"
        f"{ANSI['reset']}"
    )


# ============================================================
# OUTPUT
# ============================================================

def info(message: str) -> None:
    print(
        color(
            "[ E.V. ] ",
            "cyan",
        )
        + message
    )


def success(message: str) -> None:
    print(
        color(
            "[  OK  ] ",
            "green",
        )
        + message
    )


def warning(message: str) -> None:
    print(
        color(
            "[ WARN ] ",
            "yellow",
        )
        + message
    )


def error(message: str) -> None:
    print(
        color(
            "[ FAIL ] ",
            "red",
        )
        + message
    )


# ============================================================
# SUBPROCESS
# ============================================================

def run_git(
    *args: str,
    timeout: int = CHECK_TIMEOUT,
) -> subprocess.CompletedProcess[str]:
    """
    Execute git inside the E.V. project directory.

    Raises RuntimeError on execution failures.
    """

    git = shutil.which("git")

    if git is None:
        raise RuntimeError(
            "Git was not found in PATH."
        )

    try:
        return subprocess.run(
            [
                git,
                *args,
            ],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )

    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"Git command timed out after "
            f"{timeout} seconds."
        ) from exc

    except OSError as exc:
        raise RuntimeError(
            f"Unable to start Git: {exc}"
        ) from exc


def git_output(
    *args: str,
    timeout: int = CHECK_TIMEOUT,
) -> str:
    """
    Execute a git command and return stdout.

    Raises RuntimeError when git exits unsuccessfully.
    """

    result = run_git(
        *args,
        timeout=timeout,
    )

    if result.returncode != 0:
        message = (
            result.stderr.strip()
            or result.stdout.strip()
            or f"git exited with code "
            f"{result.returncode}"
        )

        raise RuntimeError(
            message
        )

    return result.stdout.strip()


# ============================================================
# REPOSITORY DETECTION
# ============================================================

def is_git_repository() -> bool:
    try:
        result = run_git(
            "rev-parse",
            "--is-inside-work-tree",
        )

        return (
            result.returncode == 0
            and result.stdout.strip().lower()
            == "true"
        )

    except RuntimeError:
        return False


def get_current_branch() -> str:
    """
    Return the current branch name.

    Raises RuntimeError for detached HEAD.
    """

    branch = git_output(
        "branch",
        "--show-current",
    )

    if not branch:
        raise RuntimeError(
            "E.V. is running from a detached HEAD. "
            "Automatic updating is disabled."
        )

    return branch


def get_remote_url() -> str:
    try:
        return git_output(
            "remote",
            "get-url",
            "origin",
        )

    except RuntimeError:
        return ""


# ============================================================
# WORKTREE SAFETY
# ============================================================

def has_uncommitted_changes() -> bool:
    """
    Check for staged or unstaged changes.

    Untracked files count as local changes too, because an updater
    should not assume that they can safely be overwritten or ignored.
    """

    result = run_git(
        "status",
        "--porcelain",
        "--untracked-files=all",
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip()
            or "Unable to inspect Git status."
        )

    return bool(
        result.stdout.strip()
    )


def get_status_summary() -> list[str]:
    result = run_git(
        "status",
        "--short",
        "--branch",
        "--untracked-files=all",
    )

    if result.returncode != 0:
        return []

    return [
        line
        for line in result.stdout.splitlines()
        if line.strip()
    ]


# ============================================================
# REMOTE SYNC
# ============================================================

def fetch_updates(
    branch: str,
) -> None:
    """
    Fetch the configured remote branch without modifying
    the working tree.
    """

    info(
        f"Checking origin/{branch}..."
    )

    result = run_git(
        "fetch",
        "--prune",
        "origin",
        branch,
        timeout=CHECK_TIMEOUT,
    )

    if result.returncode != 0:
        message = (
            result.stderr.strip()
            or result.stdout.strip()
            or "Git fetch failed."
        )

        raise RuntimeError(
            message
        )


def get_ahead_behind(
    branch: str,
) -> tuple[int, int]:
    """
    Return:
        (behind, ahead)

    behind = commits available remotely that are not local
    ahead   = local commits not present remotely
    """

    result = run_git(
        "rev-list",
        "--left-right",
        "--count",
        f"HEAD...origin/{branch}",
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip()
            or (
                "Unable to compare local HEAD "
                f"with origin/{branch}."
            )
        )

    values = result.stdout.strip().split()

    if len(values) != 2:
        raise RuntimeError(
            "Unexpected result while comparing "
            "local and remote commits."
        )

    ahead_from_remote = int(values[0])
    behind_remote = int(values[1])

    # For HEAD...origin/branch:
    # left count  = commits only in HEAD
    # right count = commits only in origin/branch
    return (
        behind_remote,
        ahead_from_remote,
    )


# ============================================================
# UPDATE SAFETY
# ============================================================

def can_fast_forward(
    branch: str,
) -> bool:
    """
    Return True only when the local branch can safely be updated
    without a merge or overwrite.
    """

    result = run_git(
        "merge-base",
        "--is-ancestor",
        "HEAD",
        f"origin/{branch}",
    )

    return result.returncode == 0


def update_repository(
    branch: str,
) -> bool:
    """
    Perform a fast-forward-only update.

    Returns True when an update was performed.
    """

    if has_uncommitted_changes():
        warning(
            "Local changes detected."
        )

        warning(
            "E.V. will not overwrite "
            "your working tree."
        )

        return False

    if not can_fast_forward(branch):
        warning(
            "The local branch cannot be safely "
            "fast-forwarded."
        )

        warning(
            "Local and remote history have diverged."
        )

        warning(
            "Resolve the Git state manually first."
        )

        return False

    info(
        f"Updating from origin/{branch}..."
    )

    result = run_git(
        "pull",
        "--ff-only",
        "origin",
        branch,
        timeout=CHECK_TIMEOUT,
    )

    if result.returncode != 0:

        message = (
            result.stderr.strip()
            or result.stdout.strip()
            or "Git pull failed."
        )

        error(
            message
        )

        return False

    output = (
        result.stdout.strip()
    )

    if output:
        print(output)

    success(
        "E.V. updated successfully."
    )

    return True


# ============================================================
# USER PROMPT
# ============================================================

def ask_for_update(
    current: str,
    remote: str,
) -> bool:

    print()

    print(
        color(
            "╭──────────────────────────────────────────────╮",
            "purple",
        )
    )

    print(
        color(
            "│             E . V .  //  UPDATE             │",
            "cyan",
        )
    )

    print(
        color(
            "╰──────────────────────────────────────────────╯",
            "purple",
        )
    )

    print()

    print(
        f"  Local version : {current}"
    )

    print(
        f"  Remote branch : {remote}"
    )

    print()

    while True:

        try:
            answer = input(
                color(
                    "Update E.V. now? [Y/n] ",
                    "cyan",
                )
            ).strip().lower()

        except (
            EOFError,
            KeyboardInterrupt,
        ):
            return False

        if answer in {
            "",
            "y",
            "yes",
        }:
            return True

        if answer in {
            "n",
            "no",
        }:
            return False

        print(
            color(
                "Please answer y or n.",
                "yellow",
            )
        )


# ============================================================
# UPDATE CHECK
# ============================================================

def check_for_update(
    interactive: bool = True,
) -> bool:
    """
    Check for a remote update.

    Returns True if the repository was updated.
    Returns False otherwise.
    """

    print()

    print(
        color(
            "E.V. // UPDATE CHECK",
            "cyan",
        )
    )

    print(
        color(
            "Enhanced Virtuality self-update system",
            "dim",
        )
    )

    print()

    # --------------------------------------------------------
    # Validate project
    # --------------------------------------------------------

    if not PROJECT_DIR.exists():

        error(
            f"Project directory does not exist: "
            f"{PROJECT_DIR}"
        )

        return False

    if not is_git_repository():

        error(
            "E.V. is not running inside a Git repository."
        )

        return False

    remote_url = get_remote_url()

    if not remote_url:

        warning(
            "No 'origin' remote is configured."
        )

        return False

    # --------------------------------------------------------
    # Branch
    # --------------------------------------------------------

    try:
        current_branch = (
            DEFAULT_BRANCH
            or get_current_branch()
        )

    except RuntimeError as exc:

        error(
            str(exc)
        )

        return False

    success(
        f"Repository: {PROJECT_DIR}"
    )

    success(
        f"Branch: {current_branch}"
    )

    # --------------------------------------------------------
    # Protect local work
    # --------------------------------------------------------

    status = get_status_summary()

    if len(status) > 1:
        warning(
            "Working tree contains local changes."
        )

        if interactive:
            for line in status[1:]:
                print(
                    color(
                        f"  {line}",
                        "yellow",
                    )
                )

    if has_uncommitted_changes():

        warning(
            "E.V. will not automatically update "
            "over local changes."
        )

        return False

    # --------------------------------------------------------
    # Fetch
    # --------------------------------------------------------

    try:
        fetch_updates(
            current_branch
        )

    except RuntimeError as exc:

        error(
            f"Update check failed: {exc}"
        )

        return False

    # --------------------------------------------------------
    # Compare
    # --------------------------------------------------------

    try:

        behind, ahead = get_ahead_behind(
            current_branch
        )

    except RuntimeError as exc:

        error(
            str(exc)
        )

        return False

    current_commit = git_output(
        "rev-parse",
        "--short",
        "HEAD",
    )

    remote_commit = git_output(
        "rev-parse",
        "--short",
        f"origin/{current_branch}",
    )

    print()

    info(
        f"Local commit : {current_commit}"
    )

    info(
        f"Remote commit: {remote_commit}"
    )

    # --------------------------------------------------------
    # Already current
    # --------------------------------------------------------

    if behind == 0 and ahead == 0:

        success(
            "E.V. is already up to date."
        )

        return False

    # --------------------------------------------------------
    # Local ahead / divergent
    # --------------------------------------------------------

    if ahead > 0 and behind == 0:

        warning(
            "Your local branch is ahead of origin."
        )

        warning(
            "E.V. will not rewrite local history."
        )

        return False

    if ahead > 0 and behind > 0:

        warning(
            "Local and remote branches have diverged."
        )

        warning(
            "Automatic updating is disabled."
        )

        warning(
            "Resolve the Git history manually."
        )

        return False

    # --------------------------------------------------------
    # Remote ahead
    # --------------------------------------------------------

    info(
        f"{behind} new commit(s) available."
    )

    if not can_fast_forward(
        current_branch
    ):

        warning(
            "The update is not a clean fast-forward."
        )

        return False

    if AUTO_UPDATE:

        should_update = True

    elif interactive:

        should_update = ask_for_update(
            current_commit,
            remote_commit,
        )

    else:

        should_update = False

    if not should_update:

        info(
            "Update skipped."
        )

        return False

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    return update_repository(
        current_branch
    )


# ============================================================
# RESTART
# ============================================================

def restart_e_v(
    main_script: str = MAIN_SCRIPT,
) -> int:
    """
    Restart E.V. using the same Python interpreter.

    This only happens after a successful update.
    """

    script_path = (
        PROJECT_DIR
        / main_script
    ).resolve()

    if not script_path.is_file():

        error(
            f"Cannot restart E.V.: "
            f"{script_path} was not found."
        )

        return 1

    print()

    info(
        "Restarting E.V. with the updated code..."
    )

    print()

    try:
        os.execv(
            sys.executable,
            [
                sys.executable,
                str(script_path),
                *sys.argv[1:],
            ],
        )

    except OSError as exc:

        error(
            f"Unable to restart E.V.: {exc}"
        )

        return 1

    return 0


# ============================================================
# COMMAND-LINE INTERFACE
# ============================================================

def print_help() -> None:

    print(
        """
E.V. Self Updater

Usage:
    python ev_updater.py
        Check for updates interactively.

    python ev_updater.py --check
        Check without prompting.

    python ev_updater.py --update
        Check and update automatically.

    python ev_updater.py --restart
        Restart E.V. manually.

Environment variables:
    JARVIS_PROJECT_DIR
        Project directory. Defaults to this script's directory.

    JARVIS_BRANCH
        Branch to update. Defaults to the current Git branch.

    JARVIS_AUTO_UPDATE
        Set to true/1/yes/on for non-interactive updates.

    JARVIS_UPDATE_TIMEOUT
        Git operation timeout in seconds.

    JARVIS_MAIN_SCRIPT
        E.V. entry script. Defaults to jarvis.py.
"""
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    check_only = False
    force_update = False
    restart_only = False

    for argument in sys.argv[1:]:

        if argument in {
            "--help",
            "-h",
        }:

            print_help()
            return 0

        if argument == "--check":

            check_only = True
            continue

        if argument == "--update":

            force_update = True
            continue

        if argument == "--restart":

            restart_only = True
            continue

        error(
            f"Unknown argument: {argument}"
        )

        print_help()

        return 2

    # --------------------------------------------------------
    # Restart only
    # --------------------------------------------------------

    if restart_only:

        return restart_e_v()

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    updated = check_for_update(
        interactive=not check_only,
    )

    if updated:

        # The update has happened successfully.
        # In --check mode this path is never reached.
        return restart_e_v()

    # --------------------------------------------------------
    # Explicit --update
    # --------------------------------------------------------

    if force_update:

        updated = check_for_update(
            interactive=False,
        )

        if updated:
            return restart_e_v()

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
