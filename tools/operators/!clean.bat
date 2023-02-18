@echo off
setlocal

del /q /s /f *.c
del /q /s /f *.c.original
del /q /s /f *.obj
del /q /s /f *.exe
del /q /s /f *.pdb
del /q /s /f *.out
del /q /s /f *.err

popd
endlocal