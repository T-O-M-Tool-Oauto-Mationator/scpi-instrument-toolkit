"""Tests for PXIe boot-order documentation (GitHub issue #58).

Verifies that:
1. The SMU REPL help text mentions the PXIe boot-order requirement.
2. docs/troubleshooting.md contains the PXIe detection section.
3. docs/smu.md contains the PXIe boot-order warning.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lab_instruments.mock_instruments import MockNI_PXIe_4139

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def make_repl(devices):
    from lab_instruments.src import discovery as _disc

    _disc.InstrumentDiscovery.__init__ = lambda self: None
    _disc.InstrumentDiscovery.scan = lambda self, verbose=True: devices
    from lab_instruments.repl import InstrumentRepl

    repl = InstrumentRepl()
    repl._scan_thread.join(timeout=5.0)
    repl._scan_done.wait(timeout=5.0)
    repl.devices = devices
    return repl


@pytest.fixture
def repl():
    devices = {"smu": MockNI_PXIe_4139()}
    return make_repl(devices)


class TestSmuHelpPxieBootNote:
    """SMU help text should mention PXIe boot order requirement."""

    def test_help_mentions_pxie_boot_order(self, repl, capsys):
        repl.onecmd("smu")
        out = capsys.readouterr().out
        assert "PXIe" in out, "SMU help should mention PXIe"
        assert "boot" in out.lower(), "SMU help should mention boot order"

    def test_help_mentions_power_cycle(self, repl, capsys):
        repl.onecmd("smu")
        out = capsys.readouterr().out
        assert "power cycle" in out.lower(), (
            "SMU help should tell users to power cycle the PC"
        )

    def test_help_mentions_chassis_before_pc(self, repl, capsys):
        repl.onecmd("smu")
        out = capsys.readouterr().out
        assert "BEFORE" in out, (
            "SMU help should emphasize chassis must be on BEFORE the PC"
        )


class TestTroubleshootingDoc:
    """docs/troubleshooting.md should contain a PXIe section."""

    @pytest.fixture(autouse=True)
    def load_doc(self):
        path = os.path.join(PROJECT_ROOT, "docs", "troubleshooting.md")
        with open(path, encoding="utf-8") as f:
            self.content = f.read()

    def test_pxie_heading_exists(self):
        assert "## NI PXIe-4139 not detected" in self.content

    def test_mentions_bios_post(self):
        assert "BIOS/POST" in self.content

    def test_mentions_power_cycle(self):
        assert "Power cycle" in self.content

    def test_mentions_scan(self):
        assert "`scan`" in self.content


class TestSmuDoc:
    """docs/smu.md should contain a PXIe boot-order warning."""

    @pytest.fixture(autouse=True)
    def load_doc(self):
        path = os.path.join(PROJECT_ROOT, "docs", "smu.md")
        with open(path, encoding="utf-8") as f:
            self.content = f.read()

    def test_pxie_boot_order_warning(self):
        assert "PXIe boot order" in self.content

    def test_mentions_chassis_before_pc(self):
        assert "before" in self.content.lower()
        assert "host PC boots" in self.content

    def test_links_to_troubleshooting(self):
        assert "troubleshooting.md" in self.content.lower()
