"""Tests for lab_instruments/repl/__init__.py — main() and _check_for_updates()."""

import sys
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# _check_for_updates
# ---------------------------------------------------------------------------


class TestCheckForUpdates:
    def test_unknown_version_returns_false(self, monkeypatch):
        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(repl_mod, "_REPL_VERSION", "unknown")
        result = repl_mod._check_for_updates()
        assert result is False

    def test_unknown_version_force_prints(self, monkeypatch, capsys):
        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(repl_mod, "_REPL_VERSION", "unknown")
        repl_mod._check_for_updates(force=True)
        out = capsys.readouterr().out
        assert "source" in out.lower() or "skip" in out.lower()

    def test_dev_version_returns_false(self, monkeypatch):
        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(repl_mod, "_REPL_VERSION", "1.2.3.dev4")
        result = repl_mod._check_for_updates()
        assert result is False

    def test_dev_version_force_prints(self, monkeypatch, capsys):
        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(repl_mod, "_REPL_VERSION", "1.2.3.dev4")
        repl_mod._check_for_updates(force=True)
        out = capsys.readouterr().out
        assert "nightly" in out.lower()

    def test_network_error_returns_false(self, monkeypatch):
        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(repl_mod, "_REPL_VERSION", "1.0.0")
        with patch("urllib.request.urlopen", side_effect=OSError("no network")):
            result = repl_mod._check_for_updates()
        assert result is False

    def test_empty_tags_returns_false(self, monkeypatch):
        import json

        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(repl_mod, "_REPL_VERSION", "1.0.0")
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = json.dumps([]).encode()
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = repl_mod._check_for_updates()
        assert result is False

    def test_no_semver_tags_returns_false(self, monkeypatch):
        import json

        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(repl_mod, "_REPL_VERSION", "1.0.0")
        tags = [{"name": "release-xyz"}, {"name": "not-a-version"}]
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = json.dumps(tags).encode()
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = repl_mod._check_for_updates()
        assert result is False

    def test_already_up_to_date(self, monkeypatch, capsys):
        import json

        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(repl_mod, "_REPL_VERSION", "2.0.0")
        tags = [{"name": "v1.9.9"}, {"name": "v1.0.0"}]
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = json.dumps(tags).encode()
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = repl_mod._check_for_updates(force=True)
        assert result is False
        out = capsys.readouterr().out
        assert "up to date" in out.lower()

    def test_update_available_returns_true(self, monkeypatch, capsys):
        import json

        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(repl_mod, "_REPL_VERSION", "1.0.0")
        tags = [{"name": "v2.0.0"}]
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = json.dumps(tags).encode()
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = repl_mod._check_for_updates()
        assert result is True
        out = capsys.readouterr().out
        assert "update" in out.lower() or "pip" in out.lower()

    def test_update_available_same_version(self, monkeypatch):
        import json

        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(repl_mod, "_REPL_VERSION", "1.0.0")
        tags = [{"name": "v1.0.0"}]
        mock_resp = MagicMock()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_resp.read.return_value = json.dumps(tags).encode()
        with patch("urllib.request.urlopen", return_value=mock_resp):
            result = repl_mod._check_for_updates()
        assert result is False


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


def _make_repl_class(monkeypatch):
    """Patch InstrumentRepl in repl.__init__ to avoid actual hardware scan."""
    mock_repl_instance = MagicMock()
    mock_repl_instance.scripts = {}
    mock_repl_class = MagicMock(return_value=mock_repl_instance)
    import lab_instruments.repl as repl_mod

    monkeypatch.setattr(repl_mod, "InstrumentRepl", mock_repl_class)
    return mock_repl_class, mock_repl_instance


class TestMain:
    def test_version_flag(self, monkeypatch, capsys):
        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(sys, "argv", ["scpi-repl", "--version"])
        with pytest.raises(SystemExit) as exc:
            repl_mod.main()
        assert exc.value.code == 0
        out = capsys.readouterr().out
        assert "scpi-instrument-toolkit" in out

    def test_version_flag_short(self, monkeypatch, capsys):
        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(sys, "argv", ["scpi-repl", "-V"])
        with pytest.raises(SystemExit) as exc:
            repl_mod.main()
        assert exc.value.code == 0

    def test_help_flag(self, monkeypatch, capsys):
        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(sys, "argv", ["scpi-repl", "--help"])
        with pytest.raises(SystemExit) as exc:
            repl_mod.main()
        assert exc.value.code == 0
        out = capsys.readouterr().out
        assert "--mock" in out

    def test_help_flag_short(self, monkeypatch, capsys):
        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(sys, "argv", ["scpi-repl", "-h"])
        with pytest.raises(SystemExit) as exc:
            repl_mod.main()
        assert exc.value.code == 0

    def test_update_flag(self, monkeypatch):
        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(sys, "argv", ["scpi-repl", "--update"])
        monkeypatch.setattr(repl_mod, "_check_for_updates", lambda force=False: False)
        with pytest.raises(SystemExit) as exc:
            repl_mod.main()
        assert exc.value.code == 0

    def test_no_update_runs_cmdloop(self, monkeypatch):
        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(sys, "argv", ["scpi-repl"])
        monkeypatch.setattr(repl_mod, "_check_for_updates", lambda force=False: False)
        mock_class, mock_inst = _make_repl_class(monkeypatch)
        repl_mod.main()
        mock_inst.cmdloop.assert_called_once()

    def test_update_available_exits_1(self, monkeypatch):
        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(sys, "argv", ["scpi-repl"])
        monkeypatch.setattr(repl_mod, "_check_for_updates", lambda force=False: True)
        _make_repl_class(monkeypatch)
        with pytest.raises(SystemExit) as exc:
            repl_mod.main()
        assert exc.value.code == 1

    def test_ignore_update_skips_exit(self, monkeypatch):
        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(sys, "argv", ["scpi-repl", "--ignore-update"])
        monkeypatch.setattr(repl_mod, "_check_for_updates", lambda force=False: True)
        mock_class, mock_inst = _make_repl_class(monkeypatch)
        repl_mod.main()
        mock_inst.cmdloop.assert_called_once()

    def test_mock_flag_sets_discovery(self, monkeypatch):
        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(sys, "argv", ["scpi-repl", "--mock"])
        monkeypatch.setattr(repl_mod, "_check_for_updates", lambda force=False: False)
        mock_class, mock_inst = _make_repl_class(monkeypatch)
        repl_mod.main()
        mock_inst.cmdloop.assert_called_once()

    def test_script_name_runs_script(self, monkeypatch):
        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(sys, "argv", ["scpi-repl", "my_test_script"])
        monkeypatch.setattr(repl_mod, "_check_for_updates", lambda force=False: False)
        mock_class, mock_inst = _make_repl_class(monkeypatch)
        mock_inst.scripts = {"my_test_script": ["psu set 1 5.0"]}
        repl_mod.main()
        mock_inst._run_script_lines.assert_called_once()

    def test_script_not_found_exits(self, monkeypatch, capsys):
        import lab_instruments.repl as repl_mod

        monkeypatch.setattr(sys, "argv", ["scpi-repl", "nonexistent_script"])
        monkeypatch.setattr(repl_mod, "_check_for_updates", lambda force=False: False)
        mock_class, mock_inst = _make_repl_class(monkeypatch)
        mock_inst.scripts = {}
        with pytest.raises(SystemExit) as exc:
            repl_mod.main()
        assert exc.value.code == 1
