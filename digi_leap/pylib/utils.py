"""Common utility functions."""


def dict_chunks(data, batch_size) -> list[dict]:
    """Split a dictionary into chunks for subprocesses, can't return iterators."""
    batches = []
    keys = list(data.keys())
    for i in range(0, len(data), batch_size):
        batches.append({k: data[k] for k in keys[i : i + batch_size]})
    return batches
