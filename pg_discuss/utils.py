"""Generic utility functions for pg-discuss."""

class MergeConflict(Exception):
    pass

def merge_fail_on_conflict(dict1, dict2):
    """Merge two dictionaries, failing on conflict."""
    for key in dict2.keys():
        if key in dict1:
            raise MergeConflict("key {} already exists".format(key))
        else:
            return dict(dict1, **dict2)
