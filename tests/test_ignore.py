from flexlate_dev.ignore import IgnoreSpecification


def test_ignore_file():
    ignore = IgnoreSpecification(ignore_list=["a.txt"])
    assert ignore.file_is_ignored("a.txt")
    assert not ignore.file_is_ignored("b.txt")


def test_ignore_folder():
    ignore = IgnoreSpecification(ignore_list=["a/"])
    assert ignore.file_is_ignored("a/b.txt")
    assert not ignore.file_is_ignored("b.txt")
