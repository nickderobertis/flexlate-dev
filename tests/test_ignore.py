from flexlate_dev.ignore import IgnoreSpecification


def test_ignore_file():
    ignore = IgnoreSpecification(ignore_list=["a.txt"])
    assert ignore.file_is_ignored("a.txt")
    assert not ignore.file_is_ignored("b.txt")


def test_ignore_folder():
    ignore = IgnoreSpecification(ignore_list=["a/"])
    assert ignore.file_is_ignored("a/b.txt")
    assert not ignore.file_is_ignored("b.txt")


def test_negate_ignore():
    ignore = IgnoreSpecification(ignore_list=["a/", "!a/b.txt"])
    assert ignore.file_is_ignored("a/a.txt")
    assert not ignore.file_is_ignored("a/b.txt")
    assert not ignore.file_is_ignored("b.txt")


def test_negate_ignore_that_was_previously_ignored():
    ignore = IgnoreSpecification(ignore_list=["a/", "!a/"])
    assert not ignore.file_is_ignored("a/b.txt")
    assert not ignore.file_is_ignored("a/a.txt")
    assert not ignore.file_is_ignored("b.txt")


def test_ignore_glob():
    ignore = IgnoreSpecification(ignore_list=["a/*.txt"])
    assert ignore.file_is_ignored("a/a.txt")
    assert ignore.file_is_ignored("a/b.txt")
    assert not ignore.file_is_ignored("a/a.py")
    assert not ignore.file_is_ignored("b.txt")


def test_empty_ignore_does_not_ignore_anything():
    ignore = IgnoreSpecification(ignore_list=[])
    assert not ignore.file_is_ignored("a/a.txt")
    assert not ignore.file_is_ignored("a/b.txt")
    assert not ignore.file_is_ignored("b.txt")
