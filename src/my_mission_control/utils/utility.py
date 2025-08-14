import re


def snake_to_camel(snake_str: str) -> str:
    return re.sub(r"_([a-zA-Z])", lambda match: match.group(1).upper(), snake_str)
