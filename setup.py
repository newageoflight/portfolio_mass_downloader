from cx_Freeze import setup, Executable

base = None

executables = [Executable("main.py", base=base)]

packages=["idna", "crawlers", "os", "json", "requests_html", "lxml", "tqdm", "urllib.parse", "traceback",
"multiprocessing", "pathlib", "csv", "requests"]
options = {
    "build_exe": {
        "packages": packages
    }
}

setup(
    name="Portfolio Mass Downloader",
    options=options,
    version="0.1.1.0",
    description="Downloads your entire portfolio from eMed",
    executables=executables
)