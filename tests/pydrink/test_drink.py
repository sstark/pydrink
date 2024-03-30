from pydrink.config import Config
from pydrink.drink import get_dangling_links
from pathlib import Path
from pydrink.config import BY_TARGET
from pydrink.git import get_tracked_objects


def test_get_dangling_links(monkeypatch, tracked_drinkrc_and_drinkdir, fake_home):

    def mock_home():
        return fake_home

    monkeypatch.setattr(Path, "home", mock_home)
    c = Config(tracked_drinkrc_and_drinkdir)
    for obj in get_tracked_objects(c):
        obj.link()
    (Path.home() / "bin" / "dangle1").symlink_to(c["DRINKDIR"] / "bin" / "dangle1")
    (Path.home() / ".dangle2").symlink_to(c["DRINKDIR"] / "conf" / BY_TARGET / "singold" / "dangle2")
    dangle_bin = list(get_dangling_links(c, "bin"))
    assert dangle_bin == [Path.home() / "bin" / "dangle1"]
    dangle_conf = list(get_dangling_links(c, "conf"))
    assert dangle_conf == [Path.home() / ".dangle2"]

    for obj in get_tracked_objects(c):
        assert obj.get_linkpath() not in dangle_bin
        assert obj.get_linkpath() not in dangle_conf
