def merge_dicts_preferring_non_none(*dicts: dict) -> dict:
    """
    Merge multiple dictionaries, overriding previous values with later ones
    unless the value is None. None will only be the output value if
    all the dicts have the value None for that key.
    """
    output = {}
    for d in dicts:
        for k, v in d.items():
            if k not in output or v is not None:
                output[k] = v
    return output
