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


def plot3d():
    """
    map all driving and journey time values to a
    3d graphic representation.
    """
    f = parse_file("example.txt")
    xv, yv, zv = "driving", "journey_time", "tip"
    sim_ctrl = ControllerController(f[0], f[1], flush_after_run=20*100+1)
    x, y, z = plot3dFRB(sim_ctrl.simulator, xv, yv, zv)
    make_plot(x, y, z, xv, yv, zv)


def read_ex_file(fpath):
    """
    show defuzzed consequences along with plots for all
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
    sim.print_state()


def do_experiment(label):
    if label == "1":
        read_ex_file("example.txt")
    if label == '2':
        plot3d()
    if label == "3":
        read_ex_file("example2.txt")


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
        choices=["1", "2", "3"],
        default=None,
        help="choose a premade experiment",
    )
    args = vars(parser.parse_args())
    if label := args.get("experiment"):
        do_experiment(label)
    else:
        read_ex_file(args.get("path"))
