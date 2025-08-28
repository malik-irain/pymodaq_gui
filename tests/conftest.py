import os
import pytest
from qtpy.QtWidgets import QApplication

import matplotlib
matplotlib.use("Agg")

import pyqtgraph as pg
pg.setConfigOption('useOpenGL', False)   # avoid GPU calls if unstable
pg.setConfigOption('enableExperimental', False)

# --- Headless Qt configuration ---
# os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")  # offscreen rendering
# os.environ.setdefault("QT_OPENGL", "software")          # software OpenGL

@pytest.fixture(scope="session", autouse=True)
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

# --- Monkeypatch HistogramLUTWidget globally ---
# @pytest.fixture(autouse=True)
# def mock_histogram(monkeypatch):
#     from pyqtgraph.widgets import HistogramLUTWidget
#     monkeypatch.setattr(HistogramLUTWidget, "__init__", lambda self, *a, **kw: None)
#
