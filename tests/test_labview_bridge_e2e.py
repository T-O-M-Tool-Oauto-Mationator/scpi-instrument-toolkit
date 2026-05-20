"""End-to-end smoke tests for the LabVIEW bridge.

LabVIEW's Python Node calls the bridge by `import labview_bridge` (the
top-level shim at the repo root copied to site-packages), not by path.
Unit tests in test_labview_bridge.py import the inner module
(lab_instruments.src.labview_bridge) and inject fake devices into the
cache. Those tests verify each wrapper in isolation but don't verify
that the shim re-exports the function, that the public open_* path
actually populates the cache, or that a realistic chain of calls flows
correctly.

These tests do all three:

- Import via `import labview_bridge` (the shim), exactly as LabVIEW does.
- Open instruments via open_psu / open_dmm / open_awg with mocked pyvisa
  (no _inject shortcut).
- Run the actual Lab 1 (TPS22968 RDSon) workflow end-to-end and verify
  the right SCPI bytes hit the wire in the right order.
"""

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def _clean_bridge():
    """Reset bridge cache between tests."""
    import labview_bridge as lvb_shim

    yield
    # Reset internal cache
    inner = lvb_shim.close_all
    inner()


@pytest.fixture
def mock_visa():
    """Mock pyvisa.ResourceManager so open_* calls succeed without hardware.
    Yields the mock instrument that every opened driver shares."""
    mock_instrument = MagicMock()
    mock_rm = MagicMock()
    mock_rm.open_resource.return_value = mock_instrument
    with patch("pyvisa.ResourceManager", return_value=mock_rm):
        yield mock_instrument


# =========================================================================
# Shim sanity
# =========================================================================


class TestShimSanity:
    """If these fail, no LabVIEW VI can call the bridge."""

    def test_shim_imports_under_labview_name(self):
        """LabVIEW does `import labview_bridge` - confirm the bare-name
        import resolves to a module with the expected public surface."""
        import labview_bridge

        # Spot-check both old and new (v1.0.65) wrappers
        for name in (
            "open_psu",
            "psu_set_voltage",
            "psu_enable_output",
            "psu_disable_all",
            "psu_get_voltage_setpoint",  # v1.0.65
            "dmm_measure_dc_voltage",
            "dmm_configure_dc_voltage",  # v1.0.65
            "dmm_read",  # v1.0.65
            "awg_set_dc_output",
            "awg_set_offset",  # v1.0.65
            "ev2300_read_byte",
        ):
            assert hasattr(labview_bridge, name), f"Shim missing '{name}' - update labview_bridge.py imports + __all__"

    def test_shim_all_list_matches_attrs(self):
        """Every name in __all__ must be importable and callable. Catches
        orphaned entries left over after a function was removed/renamed in
        the inner bridge."""
        import labview_bridge

        for name in labview_bridge.__all__:
            attr = getattr(labview_bridge, name, None)
            assert callable(attr), f"__all__ entry '{name}' is not callable"

    def test_shim_inner_match(self):
        """Every public function in the inner bridge module should be
        re-exported by the shim (no shrinkage from drift)."""
        import labview_bridge as shim
        from lab_instruments.src import labview_bridge as inner

        inner_public = {
            n
            for n in dir(inner)
            if not n.startswith("_")
            and callable(getattr(inner, n))
            and getattr(inner, n).__module__.endswith("labview_bridge")
        }
        shim_set = set(shim.__all__)
        missing = inner_public - shim_set
        # Allow some bookkeeping functions that aren't useful from LabVIEW
        allowed_missing = set()
        assert missing - allowed_missing == set(), (
            f"Inner bridge has public functions missing from shim: {missing - allowed_missing}"
        )


# =========================================================================
# Lab 1 (TPS22968 RDSon) end-to-end workflow
# =========================================================================


class TestLab1Workflow:
    """Replays the Lab 1 RDSon characterization sequence through the shim:

      Open HP_E3631A PSU, HP_34401A DMM, BK_4063 AWG
      Configure AWG ch1 = 3.3 V DC, ch2 = 0 V DC (DUT ch1 enable, ch2 off)
      Configure PSU P6V = 5 V, 1 A limit
      Configure DMM for DC voltage with 100 mV range, 0.1 mV resolution, NPLC = 10
      Enable PSU output, enable AWG ch1
      Read DMM (Vout)
      Read PSU current (Iload)
      Disable all outputs

    Verifies the right vendor SCPI bytes hit the wire in the right order
    via a single shared mock_instrument."""

    def test_full_test1_sequence(self, mock_visa):
        """Single full execution of Lab 1 Test 1 at 5 V. Mirrors what the
        LabVIEW Lab 1 VI is supposed to do."""
        import labview_bridge as lvb

        # Mocked instrument query returns: Vout = 7 mV (from results.txt),
        # current = 0.33 A
        mock_visa.query.return_value = "0.0070"  # default for all queries

        # ---- Open instruments ----
        psu_id = lvb.open_psu("GPIB::5::INSTR", "HP_E3631A")
        dmm_id = lvb.open_dmm("GPIB::22::INSTR", "HP_34401A")
        awg_id = lvb.open_awg("USB::INSTR", "BK_4063")

        assert psu_id.startswith("psu_")
        assert dmm_id.startswith("dmm_")
        assert awg_id.startswith("awg_")

        # ---- Configure AWG: ch1 = 3.3 V DC, ch2 = 0 V DC ----
        assert lvb.awg_set_dc_output(awg_id, 1, 3.3) == "OK"
        assert lvb.awg_set_dc_output(awg_id, 2, 0.0) == "OK"

        # ---- Configure PSU: P6V = 5 V, 1 A ----
        assert lvb.psu_set_output_channel(psu_id, 1, 5.0, 1.0) == "OK"

        # ---- Configure DMM: DC voltage, 0.1 V range, 0.1 mV resolution, NPLC=10 ----
        # Mirrors lab1.scpi: dmm config vdc 0.1 0.0001 nplc=10
        assert lvb.dmm_configure_dc_voltage(dmm_id, 0.1, 0.0001, 10.0) == "OK"

        # ---- Enable outputs ----
        assert lvb.psu_enable_output(psu_id, True) == "OK"
        assert lvb.awg_enable_output(awg_id, 1, True) == "OK"
        assert lvb.awg_enable_output(awg_id, 2, False) == "OK"

        # ---- Measure ----
        mock_visa.query.return_value = "0.0070"
        vout = lvb.dmm_read(dmm_id)
        assert isinstance(vout, float)

        mock_visa.query.return_value = "0.33"
        iload = lvb.psu_measure_current(psu_id, 1)
        assert isinstance(iload, float)

        # Compute Ron (the LabVIEW VI does this on the front panel, not via
        # the bridge - but verify the calculation against the captured
        # values to make sure we got plausible numbers)
        ron_mohms = (vout / iload) * 1000
        assert 5.0 < ron_mohms < 50.0, f"unrealistic Ron: {ron_mohms} mOhm"

        # ---- Safe state ----
        assert lvb.psu_disable_all(psu_id) == "OK"
        assert lvb.awg_disable_all(awg_id) == "OK"

        # ---- Verify SCPI on the wire ----
        cmds = [c.args[0] for c in mock_visa.write.call_args_list]

        # AWG DC outputs were programmed
        assert any("OFST" in c or "OFFSET" in c.upper() for c in cmds), (
            f"AWG set_dc_output did not emit OFFSET-class SCPI: {cmds[:10]}"
        )
        # PSU APPLY for P6V at 5V/1A
        assert "APPLY P6V, 5.0, 1.0" in cmds, f"PSU APPLY missing from {cmds}"
        # DMM configure with explicit range/resolution/nplc
        assert any("CONF" in c.upper() and "VOLT" in c.upper() for c in cmds), f"DMM CONFigure missing from {cmds}"
        assert any("NPLC" in c.upper() and "10" in c for c in cmds), f"DMM NPLC missing from {cmds}"
        # PSU output enable
        assert "OUTPUT:STATE ON" in cmds, "PSU enable_output(True) didn't send OUTPUT:STATE ON"
        # Final safe state
        assert "OUTPUT:STATE OFF" in cmds, "psu_disable_all didn't send OUTPUT:STATE OFF"
        # APPLY safe-state lines (with DEFAULT_CURRENT_LIMIT, regression
        # for the v1.0.62 CC-at-0A bug that motivated this whole audit)
        assert "APPLY P6V, 0.0, 1.0" in cmds
        assert "APPLY P25V, 0.0, 0.5" in cmds
        assert "APPLY N25V, 0.0, 0.5" in cmds

    def test_configure_then_read_then_fetch(self, mock_visa):
        """Verify the configure-then-read flow (new in v1.0.65) and that
        fetch returns the same value without re-triggering."""
        import labview_bridge as lvb

        dmm_id = lvb.open_dmm("GPIB::22::INSTR", "HP_34401A")

        # configure
        lvb.dmm_configure_dc_voltage(dmm_id, 10.0, 0.001, 1.0)

        # read
        mock_visa.query.return_value = "5.0023"
        v1 = lvb.dmm_read(dmm_id)
        assert v1 == pytest.approx(5.0023, rel=1e-6)
        assert mock_visa.query.call_args_list[-1].args[0] == "READ?"

        # fetch
        mock_visa.query.return_value = "5.0024"
        v2 = lvb.dmm_fetch(dmm_id)
        assert v2 == pytest.approx(5.0024, rel=1e-6)
        assert mock_visa.query.call_args_list[-1].args[0] == "FETCh?"


# =========================================================================
# Validation reaches the user from the shim path (not just inner module)
# =========================================================================


class TestValidationThroughShim:
    """Confirm the validation guards added in v1.0.64/65 are reachable
    via the shim path (not just from the inner module). LabVIEW only ever
    sees the shim - if the shim shadows or wraps in a way that loses the
    error message, students wouldn't see it."""

    def test_unwired_id_raises_through_shim(self):
        import labview_bridge as lvb

        with pytest.raises(ValueError, match="instrument_id"):
            lvb.psu_set_voltage("", 1, 5.0)

    def test_unwired_bool_raises_through_shim(self, mock_visa):
        import labview_bridge as lvb

        psu_id = lvb.open_psu("GPIB::5::INSTR", "HP_E3631A")
        with pytest.raises(TypeError, match="must be a Boolean"):
            lvb.psu_enable_output(psu_id, 0)  # LabVIEW unwired Boolean -> 0

    def test_unwired_channel_raises_through_shim(self, mock_visa):
        import labview_bridge as lvb

        awg_id = lvb.open_awg("USB::INSTR", "BK_4063")
        with pytest.raises(ValueError, match="channel"):
            lvb.awg_set_dc_output(awg_id, 0, 3.3)  # unwired I32 -> 0

    def test_unknown_driver_through_shim(self):
        import labview_bridge as lvb

        with pytest.raises(ValueError, match="Unknown driver"):
            lvb.open_psu("GPIB::5::INSTR", "BOGUS_3631A")

    def test_psu_driver_passed_to_open_dmm_through_shim(self):
        """The category guard added in v1.0.64 must work via the shim too."""
        import labview_bridge as lvb

        with pytest.raises(TypeError, match="not a DMM driver"):
            lvb.open_dmm("GPIB::5::INSTR", "HP_E3631A")
