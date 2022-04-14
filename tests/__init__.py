import tkinter as tk
import pytest

# running GUI testing appears to make pytest unstable; leaving
# hear until i can decide how to handle
# @pytest.fixture
# def root():
#     root_frame = tk.Tk()
#     yield root_frame
#
#     try:
#         root_frame.destroy()
#     except:
#         pass
