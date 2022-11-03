import sys
from cx_Freeze import setup, Executable

setup(
    name="MrMime2_NaoService",
    version="0.1",
    description="Naoqi server that works as a proxy between MrMime2 app and NAO robot.",
    executables=[Executable("Main.py")]
)