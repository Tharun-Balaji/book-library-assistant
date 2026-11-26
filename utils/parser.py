import json
import re


_FUNCTION_CALL_PATTERN = re.compile(r"CALL_FUNCTION:([A-Za-z_][A-Za-z0-9_]*):(.*)")


def _split_parameters(parameters_text):
    """Split parameters on commas outside JSON arrays and quoted strings."""
    parts = []
    start = 0
    bracket_depth = 0
    in_quotes = False
    escaped = False

    for index, character in enumerate(parameters_text):
        if in_quotes:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_quotes = False
        elif character == '"':
            in_quotes = True
        elif character == "[":
            bracket_depth += 1
        elif character == "]":
            bracket_depth -= 1
            if bracket_depth < 0:
                raise ValueError("Unexpected closing bracket")
        elif character == "," and bracket_depth == 0:
            parts.append(parameters_text[start:index].strip())
            start = index + 1

    if in_quotes or bracket_depth != 0:
        raise ValueError("Unterminated quoted value or array")

    parts.append(parameters_text[start:].strip())
    return parts

def parse_function_call(text):
    """
    Parse function call with intermediate complexity (arrays and optional parameters)
    
    Args:
        text (str): Text that may contain a function call
        
    Returns:
        tuple: (function_name, parameters) or (None, None) if no function call found
    """
    if not isinstance(text, str):
        return None, None

    match = _FUNCTION_CALL_PATTERN.fullmatch(text.strip())
    if match is None:
        return None, None

    function_name, parameters_text = match.groups()
    parameters = {}
    if not parameters_text.strip():
        return function_name, parameters

    try:
        for item in _split_parameters(parameters_text):
            if not item or "=" not in item:
                return None, None

            name, value = item.split("=", 1)
            name = name.strip()
            value = value.strip()
            if not name or not value or name in parameters:
                return None, None

            if value.startswith("["):
                parameters[name] = parse_array_parameter(value)
            elif value.startswith('"'):
                decoded_value = json.loads(value)
                if not isinstance(decoded_value, str):
                    return None, None
                parameters[name] = decoded_value
            elif re.fullmatch(r"-?\d+", value):
                parameters[name] = int(value)
            else:
                parameters[name] = value
    except (ValueError, json.JSONDecodeError):
        return None, None

    return function_name, parameters

def parse_array_parameter(param_str):
    """
    Parse an array parameter like ["Tokyo", "Seoul"]
    
    Args:
        param_str (str): Array parameter string
        
    Returns:
        list: Parsed array
    """
    if isinstance(param_str, list):
        values = param_str
    elif isinstance(param_str, str):
        try:
            values = json.loads(param_str.strip())
        except json.JSONDecodeError as error:
            raise ValueError("Array parameters must use JSON array syntax") from error
    else:
        raise ValueError("Array parameters must be a JSON array")

    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        raise ValueError("Array parameters must contain only strings")

    return values