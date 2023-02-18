#! /usr/bin/env python
# -*- coding: utf-8 -*-

from multiprocessing import Pool, Lock
from subprocess import run
from pathlib import Path
from time import sleep

ACTIVATE_BAT = 'C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\Community\\VC\\Auxiliary\\Build\\vcvarsall.bat'
lock = Lock()

def main():
    root = Path(__file__).parent
    
    print("Compiling files")
    with Pool() as p:
        p.map(compile, root.glob("*.c"))
        
    print("Done")
    return 0


def compile(f):
    with lock: print(f"Compiling {f}")
    c = f
    original_c = f.with_suffix(".c.original")
    obj = f.with_suffix(".obj")
    compile_out = f.with_suffix(".compile.out")
    compile_err = f.with_suffix(".compile.err")
    comment_out = f.with_suffix(".comment.out")
    comment_err = f.with_suffix(".comment.err")

    while True:
        run(f'("{ACTIVATE_BAT}" x86 && cl /nologo /Od /DDEBUG /WX /Wall /c /Fo{obj} {c}) > {compile_out} 2> {compile_err}', shell=True)
        if obj.exists() and obj.stat().st_size > 0:
            with lock: print(f"Compiled {f}")
            break
        assert compile_err.exists()
        assert compile_out.exists()
        sleep(3) # wait for cl to release everything
        run(f'python commenter.py {compile_out} -p config_msvc.json -b -o -e cp437 -E utf8 -c "// (MSVC)" > {comment_out} 2> {comment_err}', shell=True)

    for f in [compile_out, compile_err, comment_out, comment_err, obj, original_c]:
        for i in range(10):
            if f.exists():
                try:
                    f.unlink()
                    break
                except:
                    sleep(3)


if __name__ == "__main__":
    main()