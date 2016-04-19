from antminer_autotune.util import ListTraverse


def test_list_traverse():
    l = [
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80
    ]

    lt = ListTraverse(l)

    assert(lt.current() == 10)
    assert(lt.next() == 20)
    assert(lt.next() == 30)
    assert(lt.next() == 40)
    assert(lt.next() == 50)


def test_list_traverse_with_dec():
    l = [
        1.1,
        1.2,
        1.3,
        1.4,
        1.5,
        1.6,
        1.7,
        1.8
    ]

    lt = ListTraverse(l)

    assert(lt.current() == 1.1)
    assert(lt.next() == 1.2)
    assert(lt.next() == 1.3)
    assert(lt.next() == 1.4)
    assert(lt.next() == 1.5)


def test_list_traverse_with_min():
    l = [
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80
    ]

    lt = ListTraverse(l, cur_value=50, min_value=30)

    assert(lt.current() == 50)
    assert(lt.prev() == 40)
    assert(lt.prev() == 30)
    assert(lt.prev() != 20)
    assert(lt.prev() == 30)


def test_list_traverse_with_no_min():
    l = [
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80
    ]

    lt = ListTraverse(l, cur_value=20)

    assert(lt.current() == 20)
    assert(lt.prev() == 10)
    assert(lt.prev() == 10)


def test_list_traverse_with_max():
    l = [
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80
    ]

    lt = ListTraverse(l, cur_value=50, max_value=70)

    assert(lt.current() == 50)
    assert(lt.next() == 60)
    assert(lt.next() == 70)
    assert(lt.next() != 80)
    assert(lt.next() == 70)


def test_list_traverse_with_no_max():
    l = [
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80
    ]

    lt = ListTraverse(l, cur_value=70)

    assert(lt.current == 70)
    assert(lt.next() == 80)
    assert(lt.next() == 80)


def test_list_traverse_is_valid():
    l = [
        10,
        20,
        30,
        40,
        50,
        60,
        70,
        80
    ]

    lt = ListTraverse(l, min_value=30, max_value=70)

    assert(lt.is_valid(50))
    assert(not lt.is_valid(51))
    assert(not lt.is_valid(20))
    assert(not lt.is_valid(80))
