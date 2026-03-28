from typing import Any, Dict


def evaluate_condition(condition: str, context: Dict[str, Any]) -> bool:
    """Evaluate a safe Python condition against a context dict.

    Args:
        condition: Python expression as string (e.g., "scale == 'large'")
        context: Dictionary of variables available to the condition

    Returns:
        bool: Result of condition evaluation, False on any error

    Examples:
        >>> ctx = {'scale': 'large', 'domain': 'web'}
        >>> evaluate_condition("scale == 'large'", ctx)
        True
        >>> evaluate_condition("domain == 'api'", ctx)
        False
    """
    if not condition:
        return False

    try:
        safe_globals = {"__builtins__": {}}
        result = eval(condition, safe_globals, context)
        return bool(result)
    except Exception:
        return False
