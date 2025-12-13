# -*- mode: python ; coding: utf-8 -*-

from kivy_deps import sdl2, glew
import os 
import site
import sys
from setuptools._vendor import jaraco

block_cipher = None

# Change the Path correspondently for the
a = Analysis(
    [os.path.join(os.getcwd(), '..\\Signalkit\\v1\\main.py')],
    pathex=[],
    binaries=[
        (os.path.join(p, "SDL2.dll"), ".") for p in sdl2.dep_bins
    ] + [
        (os.path.join(p, "glew32.dll"), ".") for p in glew.dep_bins
    ],    
    datas=[
        (os.path.join(jaraco.__path__[0], "text", "Lorem ipsum.txt"), "jaraco/text"),
    ],
    hiddenimports=[
        "scipy.signal",
        "scipy._lib.array_api_compat.numpy.fft",
        "kivy_matplotlib_widget.uix",
        "kivy_matplotlib_widget.uix.graph_widget",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Dev/Debug/IPython-related
        'asttokens', 'debugpy', 'docutils', 'executing', 'pure_eval', 'stack_data',
        'ipykernel', 'IPython', 'jupyter_client', 'jupyter_core', 'traitlets',
        'prompt_toolkit', 'pydoc_data', 'jedi', 'parso', 'pygments', 'wcwidth',

        # Networking/HTTP
        'certifi', 'charset_normalizer', 'idna', 'urllib3',

        # Packaging/Runtime extras
        'importlib_metadata', 'importlib_metadata-8.0.0.dist-info', 'pycparser',
        'autocommand', 'colorama', 'comm', 'exceptiongroup',

        # Math/ML/Graph extras
        'jax', 'jaxlib', 'matplotlib_inline', 'mpl_toolkits', 'opt_einsum',
        'PyQt5', 'pyqtgraph', 'pooch', 'joblib', 'numba', 'llvmlite', 'scikit-learn',

        # GUI and UI not used
        'tcl', 'tcl8', 'tk', 'tkinter',

        # Standard lib extras and misc
        'test', 'tomli', 'tornado', 'typeguard', 'typeguard-4.3.0.dist-info',
        'unittest', 'wheel', 'xmlrpc', 'zipp', 'zmq'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz, Tree(os.path.join(os.getcwd(), '..\\Signalkit\\v1')),
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Signalkit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)