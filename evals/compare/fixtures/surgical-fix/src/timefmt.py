"""Small formatting helpers."""
import math


def format_duration(seconds):
    """Format whole seconds as M:SS."""
    minutes = round(seconds / 60)
    secs = seconds - minutes * 60
    return f"{minutes}:{secs:02d}"


def format_size(n):
    """Human readable size."""
    if n < 1024:
        return str(n) + " B"
    elif n < 1024 * 1024:
        return str(round(n / 1024, 1)) + " KB"
    else:
        return str(round(n / 1024 / 1024, 1)) + " MB"


def clamp(x, lo, hi):
    if x < lo: return lo
    elif x > hi: return hi
    else: return x


def pad(s, width):
    return s + " " * (width - len(s)) if len(s) < width else s
