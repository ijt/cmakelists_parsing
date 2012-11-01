
def merge_pairs(list, should_merge, merge):
    """
    >>> merge_pairs([], None, None):
    []

    >>> merge_pairs([1], None, None):
    [1]

    >>> merge_pairs([1, 2], lambda x, y: False, None)
    [1, 2]

    >>> merge_pairs([1, 2], lambda x, y: y == x + 1, lambda x, y: (x, y))
    [(1, 2)]

    >>> merge_pairs([1, 2, 3], lambda x, y: y == x + 1, lambda x, y: (x, y))
    [(1, 2), 3]

    >>> merge_pairs([1, 2, 3, 4], lambda x, y: y == x + 1, lambda x, y: (x, y))
    [(1, 2), (3, 4)]
    """
    