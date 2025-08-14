import pytest
import tomli_w

from my_mission_control.utils.pyproject_util import _find_pyproject_toml, get_pyproject_metadata


@pytest.fixture
def tmp_pyproject_toml(tmp_path):
    content = {"project": {"name": "test-project", "version": "0.1.2"}}
    pyproject_path = tmp_path / "pyproject.toml"
    with open(pyproject_path, "wb") as f:
        f.write(tomli_w.dumps(content).encode("utf-8"))
    return pyproject_path


def test_find_pyproject_toml(tmp_pyproject_toml):
    found_path = _find_pyproject_toml(tmp_pyproject_toml.parent)
    assert found_path == tmp_pyproject_toml


def test_get_pyproject_metadata_success(tmp_pyproject_toml, monkeypatch):
    monkeypatch.setattr("my_mission_control.utils.pyproject_util._find_pyproject_toml", lambda _: tmp_pyproject_toml)
    name, version = get_pyproject_metadata()
    assert name == "test-project"
    assert version == "0.1.2"


def test_get_pyproject_metadata_missing_file(monkeypatch):
    monkeypatch.setattr("my_mission_control.utils.pyproject_util._find_pyproject_toml", lambda _: None)
    name, version = get_pyproject_metadata()
    assert name is None
    assert version is None


def test_get_pyproject_missing_key(tmp_path, monkeypatch):
    content = {
        "project": {
            "name": "missing-version-project",
        }
    }
    pyproject_path = tmp_path / "pyproject.toml"
    with open(pyproject_path, "wb") as f:
        f.write(tomli_w.dumps(content).encode("utf-8"))
    monkeypatch.setattr("my_mission_control.utils.pyproject_util._find_pyproject_toml", lambda _: pyproject_path)
    name, version = get_pyproject_metadata()
    assert name is None
    assert version is None
