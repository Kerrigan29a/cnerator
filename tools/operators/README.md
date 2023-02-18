# General usage instructions

1. Generate a C file containing all the possible combinations of something.
2. Compile the generated C file with a C compiler.
3. If the compilation fails, use `commenter.py` to comment out the problematic lines.
4. Repeat steps 2 and 3 until the compilation succeeds.
5. At this point, the generated C file contains all the valid combinations of something.
6. Use the `gen_code.py` script to generate the Python source code for the Cnerator.

# Scriptes usage

1. Generate C files calling [generate_files.py](generate_files.py)
2. Build & comment loop. Call the scripts in this order:
    1. [build_msvc.py](build_msvc.py)
    2. [build_gcc.py](build_gcc.py)
    3. [build_clang.py](build_clang.py)
3. Generate Python source code calling [../gen_code.py](../gen_code.py)