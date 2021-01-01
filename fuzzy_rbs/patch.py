"""
Unfortunately the version of scikit-fuzzy is outdated and
the skfuzzy.control.ControlSystemSimulation.print_state-method
is broken. The version on the master branch is also broken but
for unknown reasons for me, so this monkey patch "fixes" the broken
print state with the newer version but keeps the rest of the code
the same.

The bug might be a python 2 only bug.

permalink to method:
https://github.com/scikit-fuzzy/scikit-fuzzy/blob/eecf303b701e3efacdc9b9066207ef605d4facaa/skfuzzy/control/controlsystem.py#L514
"""
from types import MethodType
from skfuzzy.control import Rule
from skfuzzy.control.term import Term, WeightedTerm
from skfuzzy.control.controlsystem import CrispValueCalculator


def print_state(self):
    """
    Print info about the inner workings of a ControlSystemSimulation.
    """
    if next(self.ctrl.consequents).output[self] is None:
        raise ValueError("Call compute method first.")

    print("=============")
    print(" Antecedents ")
    print("=============")
    for v in self.ctrl.antecedents:
        print("{!s:<35} = {}".format(v, v.input[self]))
        for term in v.terms.values():
            print("  - {:<32}: {}".format(term.label, term.membership_value[self]))
    print("")
    print("=======")
    print(" Rules ")
    print("=======")
    rule_number = {}
    for rn, r in enumerate(self.ctrl.rules):
        assert isinstance(r, Rule)
        rule_number[r] = "RULE #{}".format(rn)
        print("RULE #{}:\n  {!s}\n".format(rn, r))

        print("  Aggregation (IF-clause):")
        for term in r.antecedent_terms:
            assert isinstance(term, Term)
            print(
                "  - {0:<55}: {1}".format(term.full_label, term.membership_value[self])
            )
        print("    {!s:>54} = {}".format(r.antecedent, r.aggregate_firing[self]))

        print("  Activation (THEN-clause):")
        for c in r.consequent:
            assert isinstance(c, WeightedTerm)
            print("    {!s:>54} : {}".format(c, c.activation[self]))
        print("")
    print("")

    print("==============================")
    print(" Intermediaries and Conquests ")
    print("==============================")
    for c in self.ctrl.consequents:
        print("{!s:<36} = {}".format(c, CrispValueCalculator(c, self).defuzz()))

        for term in c.terms.values():
            print("  {}:".format(term.label))
            for cut_rule, cut_value in term.cuts[self].items():
                if cut_rule not in rule_number.keys():
                    continue
                print("    {:>32} : {}".format(rule_number[cut_rule], cut_value))
            accu = "Accumulate using {}".format(c.accumulation_method.__name__)
            print("    {!s:>32} : {}".format(accu, term.membership_value[self]))
        print("")


def patch_print_state(obj):
    obj.print_state = MethodType(print_state, obj)
