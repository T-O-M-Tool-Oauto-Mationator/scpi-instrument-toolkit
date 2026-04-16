"""Regression gate for InstrumentRepl memory leak.

These tests lock in the fix for the atexit-pinning bug that caused pytest to
OOM at 26+ GB on the full suite. If a future change reintroduces the leak
(atexit.register without unregister, or a reference cycle not broken by close()),
these tests fail.
"""

import gc
import weakref

import pytest

from lab_instruments.repl.shell import InstrumentRepl


@pytest.fixture
def _patch_discovery(monkeypatch):
    from lab_instruments.src import discovery as _disc

    monkeypatch.setattr(_disc.InstrumentDiscovery, "__init__", lambda self: None)
    monkeypatch.setattr(_disc.InstrumentDiscovery, "scan", lambda self, verbose=True: {})


def _build_repl() -> InstrumentRepl:
    repl = InstrumentRepl(register_lifecycle=False)
    repl._scan_thread.join(timeout=5.0)
    return repl


def test_closed_repl_is_collectible(_patch_discovery):
    """A REPL that has been close()'d must be eligible for garbage collection."""
    repl = _build_repl()
    ref = weakref.ref(repl)
    repl.close()
    del repl
    for _ in range(3):
        gc.collect()
    assert ref() is None, "InstrumentRepl was not collected after close() + gc"


def test_close_is_idempotent(_patch_discovery):
    """Calling close() twice must be safe and must not raise."""
    repl = _build_repl()
    repl.close()
    repl.close()


def test_many_repls_do_not_accumulate(_patch_discovery):
    """Creating and closing many REPLs must not grow the live instance count."""
    gc.collect()
    baseline = sum(1 for o in gc.get_objects() if isinstance(o, InstrumentRepl))

    repls = []
    for _ in range(20):
        repls.append(_build_repl())
    # Pop-and-close leaves no lingering loop variable (for-loop variables
    # remain in scope after the loop in Python and would otherwise retain
    # a reference to the last REPL).
    while repls:
        repls.pop().close()
    del repls
    for _ in range(5):
        gc.collect()

    alive = sum(1 for o in gc.get_objects() if isinstance(o, InstrumentRepl))
    assert alive <= baseline, f"REPL leak: baseline={baseline}, alive after 20 cycles={alive}"


def test_register_lifecycle_false_leaves_signal_handlers_untouched(_patch_discovery):
    """register_lifecycle=False must not replace the process SIGINT handler."""
    import signal

    prior = signal.getsignal(signal.SIGINT)
    repl = _build_repl()
    try:
        assert signal.getsignal(signal.SIGINT) is prior, (
            "register_lifecycle=False must not touch SIGINT, but the handler was replaced"
        )
    finally:
        repl.close()


def test_context_manager_calls_close(_patch_discovery):
    """Using InstrumentRepl as a context manager must call close() on exit."""
    repl = _build_repl()
    ref = weakref.ref(repl)
    with repl:
        pass
    del repl
    for _ in range(3):
        gc.collect()
    assert ref() is None, "Context-manager exit did not release the REPL"
