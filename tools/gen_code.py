# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
from collections import defaultdict
from pathlib import Path
import glob


translation = {
    "b":    "Bool",
    "uc":   "UnsignedChar",
    "sc":   "SignedChar",
    "ui":   "UnsignedInt",
    "si":   "SignedInt",
    "uSi":  "UnsignedShortInt",
    "sSi":  "SignedShortInt",
    "uLi":  "UnsignedLongInt",
    "sLi":  "SignedLongInt",
    "uLLi": "UnsignedLongLongInt",
    "sLLi": "SignedLongLongInt",
    "f":    "Float",
    "d":    "Double",
    "Ld":   "LongDouble",
}
types = set(list(translation.values()) + [
    "Pointer",
    "Array",
    "Struct"
])


INTS = {
    "Bool",
    "UnsignedChar", "SignedChar",
    "UnsignedInt", "SignedInt",
    "UnsignedShortInt", "SignedShortInt",
    "UnsignedLongInt", "SignedLongInt",
    "UnsignedLongLongInt", "SignedLongLongInt",
}

FLOATS = {
    "Float",
    "Double",
    "LongDouble",
}


def ignorable(operator, op_1, op_2, result_t):
    
    # Unary arithmetic operators
    if operator in ["++", "--"] and op_2 is None:
        if result_t in INTS and op_1 in INTS:
            return False
        if result_t in FLOATS and op_1 in FLOATS:
            return False
        if result_t == "Pointer" and op_1 == "Pointer":
            return False
        return True
    if operator in ["+", "-"] and op_2 is None:
        if result_t in INTS and op_1 in INTS:
            return False
        if result_t in FLOATS and op_1 in FLOATS:
            return False
        return True

    # Unary logical operators
    if operator == "!" and op_2 is None:
        if result_t in INTS and op_1 in INTS:
            return False
        return True
    
    # Unary bitwise operators
    if operator == "~" and op_2 is None:
        if result_t in INTS and op_1 in INTS:
            return False
        return True

    # Binary arithmetic operators
    if operator in ["+", "-"] and op_2 is not None:
        if result_t in INTS and op_1 in INTS and op_2 in INTS:
            return False
        if result_t in FLOATS and op_1 in FLOATS | INTS and op_2 in FLOATS | INTS:
            return False
        if result_t == "Pointer" and op_1 == "Pointer" and op_2 in INTS:
            return False
        return True
    if operator in ["*", "/"] and op_2 is not None:
        if result_t in INTS and op_1 in INTS and op_2 in INTS:
            return False
        if result_t in FLOATS and op_1 in FLOATS | INTS and op_2 in FLOATS | INTS:
            return False
        return True
    if operator == "%" and op_2 is not None:
        if result_t in INTS and op_1 in INTS and op_2 in INTS:
            return False
        return True
    
    # Binary comparison operators
    if operator in ["==", "!=", "<", ">", "<=", ">="] and op_2 is not None:
        if result_t in INTS:
            return False
        return True
    
    # Binary logical operators
    if operator in ["&&", "||"] and op_2 is not None:
        if result_t in INTS and op_1 in INTS and op_2 in INTS:
            return False
        return True
    
    # Binary bitwise operators
    if operator in ["&", "|", "^", "<<", ">>"] and op_2 is not None:
        if result_t in INTS and op_1 in INTS and op_2 in INTS:
            return False
        return True

    # Assignment arithmetic operators
    if operator in ["+=", "-="] and op_2 is None:
        if result_t in INTS and op_1 in INTS:
            return False
        if result_t in FLOATS and op_1 in FLOATS | INTS:
            return False
        if result_t == "Pointer" and op_1 in INTS:
            return False
        return True
    if operator in ["*=", "/="] and op_2 is None:
        if result_t in INTS and op_1 in INTS:
            return False
        if result_t in FLOATS and op_1 in FLOATS | INTS:
            return False
        return True
    if operator == "%=" and op_2 is None:
        if result_t in INTS and op_1 in INTS:
            return False
        return True
    
    # Assignment bitwise operators
    if operator in ["&=", "|=", "^=", "<<=", ">>="] and op_2 is None:
        if result_t in INTS and op_1 in INTS:
            return False
        return True
    
    raise ValueError(f"Unknown combination: {operator}, {op_1}, {op_2}, {result_t}")


    


def translate(name):
    name, _ = name.split("_")
    new_name = translation.get(name)
    if new_name:
        return new_name
    else:
        if name.startswith("p"):
            return "Pointer"
        if name.startswith("a"):
            return "Array"
        if name.startswith("struct"):
            return "Struct"
    raise ValueError("Unknown var name: {}".format(name))


def camel_case_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


by_operands = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
by_return = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))
available_common_operators = defaultdict(lambda: defaultdict(set))
available_lvalue_operators = defaultdict(lambda: defaultdict(set))

###
# Common operators
###

for filepath in glob.glob("operators/*.c"):
    print("***")
    print("* " + filepath)
    print("***")
    with open(filepath, "r") as f:
        for line in f:
            
            # Operators with arity 2
            
            m = re.match(r"^    ([a-zA-Z0-9_$]+) = ([a-zA-Z0-9_$]+) ([^ ]+) ([a-zA-Z0-9_$]+);$", line)
            if m:
                print(line.strip(), end= " -> ")
                result_t, op1_t, operator, op2_t = m.groups()
                op1_t = translate(op1_t)
                op2_t = translate(op2_t)
                result_t = translate(result_t)

                if ignorable(operator, op1_t, op2_t, result_t):
                    print("IGNORABLE")
                    continue

                print("{} = {} {} {}".format(result_t, op1_t, operator, op2_t))
                try:
                    by_operands[2][operator][op1_t][op2_t].add(result_t)
                except KeyError:
                    by_operands[2][operator][op1_t][op2_t] = set()
                    by_operands[2][operator][op1_t][op2_t].add(result_t)
                by_return[2][operator][result_t].add((op1_t, op2_t))
                available_common_operators[2][result_t].add(operator)
                continue

            # Operators with arity 1 (BEFORE)
            
            m = re.match(r"^    ([a-zA-Z0-9_$]+) = ([^ ]+) ([a-zA-Z0-9_$]+);$", line)
            if m:
                print(line.strip(), end= " -> ")
                result_t, operator, op1_t = m.groups()
                op1_t = translate(op1_t)
                result_t = translate(result_t)

                if ignorable(operator, op1_t, None, result_t):
                    print("IGNORABLE")
                    continue

                print("{} = {} {}".format(result_t, operator, op1_t))
                try:
                    by_operands[1][operator][op1_t].add(result_t)
                except AttributeError as e:
                    assert "'dict' object has no attribute 'add'" in str(e)
                    by_operands[1][operator][op1_t] = set()
                    by_operands[1][operator][op1_t].add(result_t)
                by_return[1][operator][result_t].add(op1_t)
                available_common_operators[1][result_t].add(operator)

            # Operators with arity 1 (AFTER)

            m = re.match(r"^    ([a-zA-Z0-9_$]+) = ([a-zA-Z0-9_$]+) ([^ ]+);$", line)
            if m:
                print(line.strip(), end= " -> ")
                result_t, op1_t, operator = m.groups()
                op1_t = translate(op1_t)
                result_t = translate(result_t)

                if ignorable(operator, op1_t, None, result_t):
                    print("IGNORABLE")
                    continue

                print("{} = {} {}".format(result_t, operator, op1_t))
                try:
                    by_operands[1][operator][op1_t].add(result_t)
                except AttributeError as e:
                    assert "'dict' object has no attribute 'add'" in str(e)
                    by_operands[1][operator][op1_t] = set()
                    by_operands[1][operator][op1_t].add(result_t)
                by_return[1][operator][result_t].add(op1_t)
                available_common_operators[1][result_t].add(operator)

            # Casts
            
            operator = "()"            
            m = re.match(r"^    ([a-zA-Z0-9_$]+) = \(\([^)]+\) ([a-zA-Z0-9_$]+)\);$", line)
            if m:
                print(line.strip(), end=" -> ")
                result_t, op1_t = m.groups()
                op1_t = translate(op1_t)
                result_t = translate(result_t)

                print("{} = (cast) {}".format(result_t, op1_t))
                try:
                    by_operands[1][operator][op1_t].add(result_t)
                except AttributeError as e:
                    assert "'dict' object has no attribute 'add'" in str(e)
                    by_operands[1][operator][op1_t] = set()
                    by_operands[1][operator][op1_t].add(result_t)
                by_return[1][operator][result_t].add(op1_t)
                available_common_operators[1][result_t].add(operator)

            # Complex assignment operators
            
            m = re.match(r"^    ([a-zA-Z0-9_$]+) ([^ ]+=) ([a-zA-Z0-9_$]+);$", line)
            if m:
                print(line.strip(), end= " -> ")
                result_t, operator, op1_t = m.groups()
                op1_t = translate(op1_t)
                result_t = translate(result_t)

                if ignorable(operator, op1_t, None, result_t):
                    print("IGNORABLE")
                    continue

                print("{} {} {}".format(result_t, operator, op1_t))
                try:
                    by_operands[1][operator][op1_t].add(result_t)
                except AttributeError as e:
                    assert "'dict' object has no attribute 'add'" in str(e)
                    by_operands[1][operator][op1_t] = set()
                    by_operands[1][operator][op1_t].add(result_t)
                by_return[1][operator][result_t].add(op1_t)
                available_common_operators[1][result_t].add(operator)

###
# Pointer operators
###
for t in types:

    # Filter types
    # if t != "SignedShortInt":
    #     continue

    data = [
        ("Pointer", "&", t),
        (t, "*", "Pointer"),
        (t, ".", "Struct"),
        (t, "->", "Struct"),
    ]
    for result_t, operator, op1_t in data:
        # by_operands[1][operator][op1_t].add(result_t if operator == "&" else None)
        # by_return[1][operator][result_t].add(op1_t)
        available_common_operators[1][result_t].add(operator)
        if operator != "&":
            available_lvalue_operators[1][result_t].add(operator)


###
# Array operator
###
op1_t = "Array"
operator = "[]"
for op2_t in [t for t in types if "Int" in t]: # Selects all subtypes of Ints

    for result_t in types:

        # by_operands[2][operator][op1_t][op2_t].add(None)
        # by_return[2][operator][result_t].add((op1_t, op2_t))
        available_common_operators[2][result_t].add(operator)
        available_lvalue_operators[2][result_t].add(operator)


###
# Compose a dict that returns the return type based on the operands types
###
by_operands_dict_parts = []
by_operands_dict_parts.append("{")
for k_arity, v_arity in sorted(by_operands.items()):
    by_operands_dict_parts.append("    {}: {{".format(k_arity))
    for k_operator, v_operator in sorted(v_arity.items()):
        by_operands_dict_parts.append("        '{}': {{".format(k_operator))
        for k_op1, v_op1 in sorted(v_operator.items()):
            if k_arity == 1:
                by_operands_dict_parts.append("            {}: [".format(k_op1))
                for data in sorted(v_op1):
                    op1_t = data
                    by_operands_dict_parts.append("                {},".format(data))
                by_operands_dict_parts.append("            ],")
            else:
                by_operands_dict_parts.append("            {}: {{".format(k_op1))
                for k_op2, v_op2 in sorted(v_op1.items()):
                    by_operands_dict_parts.append("                {}: [".format(k_op2))
                    for data in sorted(v_op2):
                        op1_t = data
                        by_operands_dict_parts.append("                    {},".format(data))
                    by_operands_dict_parts.append("                ],")
                by_operands_dict_parts.append("            },")
        by_operands_dict_parts.append("        },")
    by_operands_dict_parts.append("    },")
by_operands_dict_parts.append("}")


###
# Compose a dict that returns a list with all the possible combinations of the operands types based on the return type
###
by_return_dict_parts = []
by_return_dict_parts.append("{")
for k_arity, v_arity in sorted(by_return.items()):
    by_return_dict_parts.append("    {}: {{".format(k_arity))
    for k_operator, v_operator in sorted(v_arity.items()):
        by_return_dict_parts.append("        '{}': {{".format(k_operator))
        for k_return, v_return in sorted(v_operator.items()):
            by_return_dict_parts.append("            {}: [".format(k_return))
            for data in sorted(v_return):
                if k_arity == 1:
                    op1_t = data
                    by_return_dict_parts.append("                {},".format(data))
                else:
                    op1_t, op2_t = data
                    by_return_dict_parts.append("                ({}, {}),".format(op1_t, op2_t))
            by_return_dict_parts.append("            ],")
        by_return_dict_parts.append("        },")
    by_return_dict_parts.append("    },")
by_return_dict_parts.append("}")


with open("./operators_types.py", "w") as f:
    f.write("""# -*- coding: utf-8 -*-

# WARNING: This file has been generated with
#    {program}

'''
This module defines the types of C experessions, relative to the syntax of the C operators.
It only contains data, no computation.
Data are two dictionaries: ``by_operands`` (depending on the operator) and ``by_return`` (returned by an operator).
'''


{type_imports}

###
# By operand types
###

by_operands = {by_operands}

###
# By return type
###

by_return = {by_return}
""".format(
        program=Path(__file__),
        type_imports="\n".join("from core.ast import " + cls for cls in sorted(set(types))),
        by_operands="\n".join(by_operands_dict_parts),
        by_return="\n".join(by_return_dict_parts),
    ))

def compose_ops(ops):
    if ops:
        ops = list(sorted(ops))
        amount_ops = len(ops)
        pairs = [(op, "fr('1/{}')".format(amount_ops)) for op in ops]
        return "\n  " + ",\n  ".join('{}: {}'.format(op, prob) for op, prob in pairs) + "\n"
    else:
        return ""


available_common_operators_parts = []
for ret_t in sorted(types):
    type_ops = []
    for arity in range(1, 4):
        if arity == 3:
            # Filter types
            # XXX: If you want to exclude the Int generation, don't allow ternary operator because it uses Int in the first operand
            # ops = ""
            type_ops += [(str("?:"), arity)]
        elif arity not in available_common_operators or ret_t not in available_common_operators[arity]:
            type_ops += []
        else:
            type_ops += [(str(op), arity)
                for op in available_common_operators[arity][ret_t]
                if op not in ['+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>=']
            ]
    ret_t = camel_case_to_snake_case(ret_t)
    available_common_operators_parts.append("{}_normal_operators = {{{}}}".format(ret_t, compose_ops(type_ops)))
    available_common_operators_parts.append("if {}_normal_operators:".format(ret_t))
    available_common_operators_parts.append("  assert sum({}_normal_operators.values()) == 1".format(ret_t))
    available_common_operators_parts.append("")

available_assignment_operators_parts = []
for ret_t in sorted(types):
    arity = 1
    if arity not in available_common_operators or ret_t not in available_common_operators[arity]:
        ops = []
    else:
        ops = []
        for op in sorted(available_common_operators[arity][ret_t]):
            if op in ['+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>=']:
                ops.append((str(op), arity))
    ret_t = camel_case_to_snake_case(ret_t)
    available_assignment_operators_parts.append("{}_assignment_operators = {{{}}}".format(ret_t, compose_ops(ops)))
    available_assignment_operators_parts.append("if {}_assignment_operators:".format(ret_t))
    available_assignment_operators_parts.append("  assert sum({}_assignment_operators.values()) == 1".format(ret_t))
    available_assignment_operators_parts.append("")

available_lvalue_parts = []
for ret_t in sorted(types):
    type_ops = []
    for arity in range(1, 3):
        type_ops += [(str(op), arity) for op in available_lvalue_operators[arity][ret_t]]
    ret_t = camel_case_to_snake_case(ret_t)
    available_lvalue_parts.append("{}_lvalue_operators = {{{}}}".format(ret_t, compose_ops(type_ops)))
    available_lvalue_parts.append("if {}_lvalue_operators:".format(ret_t))
    available_lvalue_parts.append("  assert sum({}_lvalue_operators.values()) == 1".format(ret_t))
    available_lvalue_parts.append("")


with open("./operators.py", "w") as f:
    f.write("""# -*- coding: utf-8 -*-

# WARNING: This file has been generated with
#    {program}

'''
This module defines the way expressions are built, relative to the syntax of the C operators.
You can modify them to change the way expressions are created.
HOWEVER, do not change their names, since a naming convention is used (i.e., reflection).
'''

from fractions import Fraction as fr

###
# Lvalue operators
###

{lvalue}

###
# Complex assignment operators
###

{assignment}

###
# Normal operators
###

{operators}
""".format(
        program=Path(__file__),
        lvalue="\n".join(available_lvalue_parts),
        assignment="\n".join(available_assignment_operators_parts),
        operators="\n".join(available_common_operators_parts)
    ))
