from fuzzy_rbs.file_parser import parse_file
from fuzzy_rbs.fuzz import ControllerController
from fuzzy_rbs.visualize import plot3dFRB, make_plot

help_text = """
Required file format described below:

<RuleBaseName>
Rule 1:	if <variable-1> is <value_1> [and|or] [<variable-n> is <value-n>] then <variable-i> is <value-j>
Rule 2:	if <variable-2> is <value-2> [and|or] [<variable-n> is <value-n>] then <variable-i> is <value-j>
...

<variableName1>
<valueName1> <4Tuple1>
...
<valueName1> <4Tuple1>

<variableName-1> = <RealValue-1>
...
<variableName-n> = <RealValue-n>
"""


def plot3d(fpath, verbose):
    """
    Although this function look generic in parts,
    plot3dFBR is not generic and requires the variables
    values to the same as example.txt
    """
    rules, values, _ = parse_file(fpath)
    its = []
    if len(rules.antecedents) != 2 or len(rules.consequents) != 1:
        raise ValueError(
            "can only 3d graph simulations with 2 antecedents and 1 consequent"
        )
    for v in values:
        if v.name in rules.antecedents:
            its.append(
                max(y for x in v.values.values() for y in x)
                - min(y for x in v.values.values() for y in x)
            )
    iterations = its[0] * its[1] + 1
    sim_ctrl = ControllerController(rules, values, flush_after_run=iterations)
    xv, yv = list(x.label for x in sim_ctrl.ctrl.antecedents)
    zv, *_ = list(x.label for x in sim_ctrl.ctrl.consequents)
    x, y, z = plot3dFRB(sim_ctrl.simulator, xv, yv, zv)
    make_plot(x, y, z, xv, yv, zv)


def read_ex_file(fpath, verbose):
    """
    show defuzzed consequents along with plots for all
    fuzzy variable membership functions with membership level
    highlighted.
    """
    rules, variables, measurements = parse_file(fpath)
    sim = ControllerController(rules, variables)
    for measurement in measurements:
        sim.add_measurement(measurement.name, measurement.value)
    for var in sim.ctrl.consequents:
        defuzzed = sim.defuzz(var.label)
        print(f"{var.label} defuzzied is {defuzzed}")
    for var in sim.ctrl.fuzzy_variables:
        sim.view(var)
    if verbose:
        sim.print_state()


def do_experiment(label, verbose):
    if label == "tipping":
        read_ex_file("example.txt", verbose)
    if label == "3d":
        plot3d("example.txt", verbose)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="fuzzy logic system", formatter_class=argparse.RawTextHelpFormatter
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "-f",
        "--path",
        help=f"path to file containing rulebase, variable values and measurements\n{help_text}",
        default=None,
    )
    group.add_argument(
        "-e",
        "--experiment",
        choices=["tipping", "3d"],
        default=None,
        help="choose a premade experiment",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="print additional state information",
    )
    args = vars(parser.parse_args())
    verbose = args.get("verbose")
    if label := args.get("experiment"):
        do_experiment(label, verbose)
    else:
        read_ex_file(args.get("path"), verbose)
