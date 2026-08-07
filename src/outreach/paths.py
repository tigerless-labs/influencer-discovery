import os
from pathlib import Path

SKILL = "outreach"


def _dir(env_var, default):
    return Path(os.environ.get(env_var) or default).expanduser()


def config_dir():
    return _dir("OUTREACH_CONFIG_DIR", Path.home() / ".config" / SKILL)


def state_dir():
    return _dir("OUTREACH_STATE_DIR", Path.home() / ".local" / "share" / SKILL)


def memory_dir():
    return _dir("OUTREACH_MEMORY_DIR", Path.home() / "Documents" / SKILL)


def repo_dir():
    return Path(__file__).resolve().parents[2]


def repo_config_dir():
    return repo_dir() / "config"


def load_env():
    env_file = config_dir() / ".env"
    if not env_file.exists():
        return {}
    values = {}
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        values[key.strip()] = value.strip()
    return values


def credential(name):
    return os.environ.get(name) or load_env().get(name)
