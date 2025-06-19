def combine_into(delta: dict, combined: dict) -> None:
    """
    Recursively combine dictionaries together, with `delta` taking priority in choosing the value for non-dict entries.

    Stolen from https://stackoverflow.com/a/70310511
    """
    for k, v in delta.items():
        if isinstance(v, dict):
            combine_into(v, combined.setdefault(k, {}))
        else:
            combined[k] = v
