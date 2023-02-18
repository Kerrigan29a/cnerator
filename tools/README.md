# Source code generation tools

Thes tools are used to generate source code for the Cnerator.
Particulary [operators_types.py](../core/operators_types.py) and [operators.py](../core/operators.py).

# General usage instructions

1. Generate a C file containing all the possible combinations of something.
    - Process the `ttpl` files with [Templite](https://github.com/Kerrigan29a/templite).
2. Compile the generated C file with a C compiler.
3. If the compilation fails, use `commenter.py` to comment out the problematic lines.
4. Repeat steps 2 and 3 until the compilation succeeds.
5. At this point, the generated C file contains all the valid combinations of something.
6. Use the `gen_code.py` script to generate the Python source code for the Cnerator.	