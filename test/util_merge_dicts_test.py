from antminer_autotune.util import merge_dicts


def test_merge_dicts():
    d1 = {
        'key1': 'val1',
        'key2': 'val2'
    }

    d2 = {
        'key3': 'val3',
        'key4': 'val4'
    }

    expected = {
        'key1': 'val1',
        'key2': 'val2',
        'key3': 'val3',
        'key4': 'val4'
    }

    assert(merge_dicts(d1, d2) == expected)


def test_merge_dicts_overwrite():
    d1 = {
        'key1': 'val1',
        'key2': 'val2'
    }

    d2 = {
        'key2': 'val3',
        'key3': 'val3',
        'key4': 'val4'
    }

    expected = {
        'key1': 'val1',
        'key2': 'val3',
        'key3': 'val3',
        'key4': 'val4'
    }

    assert(merge_dicts(d1, d2) == expected)
