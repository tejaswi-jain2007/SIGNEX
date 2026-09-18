import os
import sys
import ctypes

# Windows DLL Bootstrap for Python 3.13 & MSVC 14.44 Runtime
if sys.platform == "win32":
    # 1. Look for PyQt6 Qt6 bin directory which contains modern MSVC runtime DLLs
    candidate_dirs = [
        os.path.join(sys.prefix, "Lib", "site-packages", "PyQt6", "Qt6", "bin"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Python", f"Python{sys.version_info.major}{sys.version_info.minor}", "Lib", "site-packages", "PyQt6", "Qt6", "bin"),
        r"C:\Users\rajde\AppData\Local\Programs\Python\Python313\Lib\site-packages\PyQt6\Qt6\bin",
    ]
    for qt_bin in candidate_dirs:
        if os.path.exists(qt_bin):
            try:
                os.add_dll_directory(qt_bin)
            except Exception:
                pass
            for dll_name in ['vcruntime140.dll', 'vcruntime140_1.dll', 'msvcp140.dll', 'msvcp140_1.dll', 'msvcp140_2.dll', 'msvcp140_atomic_wait.dll']:
                dll_path = os.path.join(qt_bin, dll_name)
                if os.path.exists(dll_path):
                    try:
                        ctypes.CDLL(dll_path)
                    except Exception:
                        pass
            break

# Ensure headless Qt operation during pytest runs
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
