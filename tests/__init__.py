import tkinter as tk
import pytest


@pytest.fixture
def root():
    root_frame = tk.Tk()
    yield root_frame

    try:
        root_frame.destroy()
    except:
        pass
