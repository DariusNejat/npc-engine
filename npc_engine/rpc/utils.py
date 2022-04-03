"""Utility functions for RPC communication."""
from typing import Any, Dict, Callable
import subprocess


def schema_to_json(
    s: Dict[str, Any], fill_value: Callable[[str], Any] = lambda _: ""
) -> Dict[str, Any]:
    """Iterate the schema and return simplified dictionary."""
    if "type" not in s and "anyOf" in s:
        return fill_value(s["title"])
    elif s["type"] == "object":
        return {k: schema_to_json(v) for k, v in s["properties"].items()}
    elif s["type"] == "array":
        return [schema_to_json(s["items"])]


def start_test_server(port: str, models_path: str):
    """Start the test server.

    Args:
        port: The port to start the server on.
        models_path: The path to the models.
    """
    subprocess.Popen(
        [
            "npc-engine",
            "--verbose",
            "run",
            "--port",
            port,
            "--models-path",
            models_path,
        ],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
