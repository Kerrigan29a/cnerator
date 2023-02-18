@echo off
setlocal
pushd "%~dp0"
python build_msvc.py
python build_gcc.py
python build_clang.py
popd
endlocal