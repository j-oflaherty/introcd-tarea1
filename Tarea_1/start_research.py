import os

if "Tarea_1" in os.getcwd():
    os.chdir("..")

    get_ipython().run_line_magic("load_ext", "autoreload")
    get_ipython().run_line_magic("autoreload", "2")

# %%
