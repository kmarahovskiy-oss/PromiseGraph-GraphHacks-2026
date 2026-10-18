"""ONLY for automated browser layout checks, NOT a real graph demo."""
from test_api import FauxStore
from promisegraph.app import create_app
app=create_app(FauxStore())
