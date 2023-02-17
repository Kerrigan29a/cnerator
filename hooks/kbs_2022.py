from core import probs, probs_helper, ast

DISTRIBUTION = None
OLD_REUSE_PROC_PROB = dict(probs.reuse_proc_prob)
OLD_REUSE_FUNC_PROB = dict(probs.reuse_func_prob)



def on_prog(args):
    raise Exception("This hook should be called only with --functions option")


def on_prog_with_function_distribution(distribution, args, remove_unwanted_functions):
    global DISTRIBUTION
    DISTRIBUTION = distribution


def on_func(program, function, return_type):
    # If the return type overpopulated, forze reuse
    remaining = calculate_remaining(program)
    try:
        if remaining[return_type.__class__] <= 0:
            if isinstance(return_type, ast.Void):
                probs.reuse_proc_prob = {True: 1, False: 0}
            else:
                probs.reuse_func_prob = {True: 1, False: 0}
        else:
            probs.reuse_proc_prob = {True: 0.70, False: 0.3}
            probs.reuse_func_prob = {True: 0.70, False: 0.3}
    except KeyError:
        probs.reuse_func_prob = {True: 1, False: 0}


def on_stmt(program, function, stmt_depth):
    # Recalculate return types probs
    remaining = calculate_remaining(program)
    for cls in remaining:
        if remaining[cls] < 0:
            remaining[cls] = 1
        else:
            remaining[cls] *= 2
    probs.return_types_prob = probs_helper.compute_proportional_prob(remaining)


def on_expr(program, function, exp_type, exp_depth_prob):
    pass


def calculate_remaining(program):
    d = {}
    for info in DISTRIBUTION.values():
        cls = getattr(ast, info["type"])
        for f in program.functions:
            d[cls] = d.get(cls, 0) + info["condition"](f)
        d[cls] = info["total"] - d.get(cls, 0)
    return d