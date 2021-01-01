import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# from skfuzzy.control.controlsystem import CrispValueCalculator

from fuzzy_rbs.file_parser import Variable, RuleBase
from fuzzy_rbs.patch import patch_print_state
from operator import or_, and_


class ControllerController:
    def __init__(self, rules: RuleBase, variables: list[Variable], **kwargs) -> None:
        self.antecedents = [
            self._parse_variable(v.name, v.values, ctrl.Antecedent)
            for v in variables
            if v.name in rules.antecedents
        ]
        self.consequents = [
            self._parse_variable(v.name, v.values, ctrl.Consequent)
            for v in variables
            if v.name in rules.consequents
        ]
        self.rules = [
            self._parse_rule(rule, self.antecedents + self.consequents)
            for rule in rules.rules.values()
        ]
        self.ctrl = ctrl.ControlSystem(self.rules)
        self.simulator = ctrl.ControlSystemSimulation(self.ctrl, **kwargs)
        patch_print_state(self.simulator)

    def _parse_rule(self, rule: dict[str, str], variables):
        labels = {v.label: v for v in variables}
        antecedent = self._interpret_term(rule["antecedent"].split(), labels)
        consequent = self._interpret_term(rule["consequent"].split(), labels)
        return ctrl.Rule(antecedent, consequent)

    def _interpret_term(self, term, vars):
        """
        recursively gather terms and use conjunction to create a single
        term.

        NOTE: Slight duplicate work here due to the parsing module now also
        identifying variables and values due to needing to identify
        antecedents and consequents from the rulebase and not the values list.
        """
        iconj = self._find_conj(term)
        if iconj is not False:
            sub_term = self._compile_term(term[:iconj], vars)
            conj = self._match_conj(term[iconj])
            return conj(sub_term, self._interpret_term(term[iconj + 1 :], vars))
        return self._compile_term(term, vars)

    def _find_conj(self, words):
        for i, word in enumerate(words):
            if self._is_conj(word):
                return i
        return False

    def _match_conj(self, conj):
        if conj == "or":
            return or_
        if conj == "and":
            return and_
        raise ValueError("unknown conjunction")

    def _compile_term(self, term, vars):
        var = term[0]
        val = term[2]
        tmp = vars.get(var)
        if tmp is None or val not in tmp.terms:
            raise ValueError(f"error in rule {term}, not in known variables: {vars}")
        return tmp[val]

    def _is_conj(self, word):
        return word == "and" or word == "or"

    def _parse_variable(
        self,
        vname: str,
        values: dict[str, tuple],
        var_constructor,
    ):
        raw_values = [val for tup in values.values() for val in tup]
        mmax = max(raw_values)
        mmin = min(raw_values)
        variable = var_constructor(np.arange(mmin, mmax, 1), vname)
        for key, value in values.items():
            variable[key] = fuzz.trapmf(variable.universe, value)
        return variable

    def add_measurement(self, variable, value) -> None:
        self.simulator.input[variable] = value

    def defuzz(self, variable):
        self.simulator.compute()
        return self.simulator.output[variable]

    def view(self, variable):
        variable.view(sim=self.simulator)

    def print_state(self):
        self.simulator.print_state()

    # def crispy_values(self, variable):
    #     crispy = CrispValueCalculator(variable, self.simulator)
    #     _, output_mf, cut_mfs = crispy.find_memberships()
    #     if len(cut_mfs) > 0 and not all(output_mf == 0):
    #         crisp_value = None
    #         if hasattr(variable, "input"):
    #             crisp_value = variable.input[self.simulator]
    #         elif hasattr(variable, "output"):
    #             crisp_value = variable.output[self.simulator]
    #         for key, term in variable.terms.items():
    #             if key in cut_mfs:
    #                 return fuzz.interp_membership(
    #                     variable.universe, term.mf, crisp_value
    #                 )
