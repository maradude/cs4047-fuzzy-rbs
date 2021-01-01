"""
file is read top to bottom and rulebase is expected before variables
Any lines matching format '<word> = <number>' are treated as measurements

expected structure

For the rulebase:

<RuleBaseName>
Rule 1:	if <variable-1> is <value_1> [and|or] [<variable-n> is <value-n>] then <variable-i> is <value-j>
Rule 2:	if <variable-2> is <value-2> [and|or] [<variable-n> is <value-n>] then <variable-i> is <value-j>
...

For setting up the fuzzy sets for each variable:
<variableName1>
<valueName1> <4Tuple1>
...
<valueName1> <4Tuple1>

And for the measurements:
<variableName-1> = <RealValue-1>
...
<variableName-n> = <RealValue-n>
"""
from dataclasses import dataclass, field
from io import TextIOWrapper
from parse import parse, findall


measurement_fstring = "{name} = {value:g}"
value_fstring = "{name} {tuple}"
rule_fstring = "{name}: if {antecedent} then {consequent}"
variable = "{name:w} is {value:w}"


@dataclass
class RuleBase:
    name: str = ""
    rules: list[dict[str, str]] = field(default_factory=dict)
    antecedents: list[str] = field(default_factory=set)
    consequents: list[str] = field(default_factory=set)


@dataclass
class Variable:
    name: str
    values: dict[str, tuple[int]]


@dataclass
class Measurement:
    name: str
    value: int


def parse_file(filename):
    """
    parse file for rulebase, variables, measurements
    expected order rulebase > variable > measurements
    """
    with open(filename, "r") as f:
        rules = parse_rule_base(f)
        variables, measurements = parse_variables_measurements(f)
    return rules, variables, measurements


def next_non_empty_line(buffer: TextIOWrapper) -> str:
    """
    return the next non-whitespace only line
    """
    for line in buffer:
        if line.strip():
            return line


def parse_rule_base(buffer: TextIOWrapper) -> RuleBase:
    """
    parse rulebase name and rules along with which variables
    are antecedents and which are consequences.
    Stops parsing on first empty line after the first rule is parsed
    """
    rule_base = RuleBase()

    line = next_non_empty_line(buffer).strip()
    if len(line.split()) != 1:
        print(f"error parsing, expected rulebase name, got: {line}")
        raise ValueError
    rule_base.name = line

    line = next_non_empty_line(buffer)
    while line:
        tmp = parse(rule_fstring, line)
        if tmp is None:
            print(f"error parsing line: {line}")
        rname = tmp.named.pop("name")
        rule_base.antecedents |= {v.named['name'] for v in findall(variable, tmp.named['antecedent'])}
        rule_base.consequents |= {v.named['name'] for v in findall(variable, tmp.named['consequent'])}
        rule_base.rules[rname] = tmp.named
        line = next(buffer).strip()

    return rule_base


def parse_variables_measurements(buffer):
    """
    read variables and measurements.

    All variables need to appear before the measurements
    """
    variables = []
    measurements = []
    line = next_non_empty_line(buffer).strip()
    while not (measurement := parse(measurement_fstring, line)):
        if len(line.split()) == 1:
            vname = line
            vvalues = gather_values(buffer)
            variables.append(Variable(vname, vvalues))
            line = next_non_empty_line(buffer).strip()
    measurements.append(
        Measurement(measurement.named["name"], measurement.named["value"])
    )
    for line in buffer:
        measurement = parse(measurement_fstring, line)
        if not measurement:
            print(f"parsing error, measurement failed to parse: {measurement}")
            raise ValueError
        measurements.append(
            Measurement(measurement.named["name"], int(measurement.named["value"]))
        )
    return variables, measurements


def gather_values(buffer):
    """
    gather all variable values and their membership function values
    until first empty line is met.
    """
    values = {}
    line = next_non_empty_line(buffer)
    while clean_line := line.strip():
        value = parse(value_fstring, clean_line)
        if not value:
            print(f"error parsing variable value: {clean_line}")
            raise ValueError
        values[value.named["name"]] = reformat_4tuple(value.named["tuple"])
        line = next(buffer)

    return values


def reformat_4tuple(tup_string):
    """
    convert between (a, b, a-offset_a, b+offset_b)
    to the 4 exact trapezoid corner x-coords.
    """
    a, b, alpha, beta = map(int, tup_string.split())
    return a - alpha, a, b, b + beta
