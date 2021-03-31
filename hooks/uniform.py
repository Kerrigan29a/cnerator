from core import probs, probs_helper


def on_prog(args):
    pass

def on_prog_with_function_distribution(distribution, args, remove_unwanted_functions):
    pass


def on_func(program, function, return_type):
    pass


def on_stmt(program, function, stmt_depth):
    # Recalculate return types probs
    d = {cls: 1 for cls in probs.return_types_prob}
    for f in program.functions:
        try:
            d[f.return_type.__class__] *= 2
        except KeyError:
            continue
    probs.return_types_prob = probs_helper.compute_inverse_proportional_prob(d)


def on_expr(program, function, exp_type, exp_depth_prob):
    pass