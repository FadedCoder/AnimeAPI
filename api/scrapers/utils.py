import re


def atoi(text):
    return int(text) if text.isdigit() else text


def kwargs2dict(*args, **kwargs):
    return kwargs


def natural_keys(k):
    # Natural sorting. Edited for use.
    return [atoi(c) for c in re.split(r'(\d+)', k['number'] or '1')]
