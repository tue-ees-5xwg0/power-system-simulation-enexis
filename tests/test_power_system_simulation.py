import json
import pprint
import unittest
import warnings

import numpy as np
import pandas as pd

with warnings.catch_warnings(action="ignore", category=DeprecationWarning):
    # suppress warning about pyarrow as future required dependency
    from pandas import DataFrame

from power_grid_model.utils import json_deserialize, json_serialize

import power_system_simulation.graph_processing as GP
import power_system_simulation.power_grid_calculation as PGC
from power_system_simulation.power_system_simulation import (
    ev_penetration_level,
    input_data_validity_check,
    n1_calculation,
    optimal_tap_position,
)


class TestMyClass(unittest.TestCase):
    def test_ini_case1(self):
        path0 = "tests/data/small_network/input/input_network_data.json"
        path1 = "tests/data/small_network/input/meta_data.json"
        path2 = "tests/data/small_network/input/active_power_profile.parquet"
        path3 = "tests/data/small_network/input/reactive_power_profile.parquet"
        path4 = "tests/data/small_network/input/ev_active_power_profile.parquet"
        pss = input_data_validity_check(path0)
        try:
            # call the class.function, if there is an error then record it
            pss.check_grid(path1)
            pss.check_graph()
            pss.check_matching(path2, path3, path4)
            pss.check_ev_charging_profiles()
        except Exception as e:
            # if there is an error, print the information and continue to next test case
            print("ini_case1() raise custom error:", e.__class__.__name__)
            print("detail:", e)
            pass

    def test_ini_case2(self):
        path0 = "tests/data/small_network/input/input_network_data.json"
        path1 = "tests/data/small_network/input/meta_data.json"
        path2 = "tests/data/small_network/input/active_power_profile.parquet"
        path3 = "tests/data/small_network/input/reactive_power_profile.parquet"
        path4 = "tests/data/small_network/input/ev_active_power_profile.parquet"
        ev = ev_penetration_level(path0, path2, path3, path4, path1)
        try:
            # call the class.function, if there is an error then record it
            tables = ev.calculate(0.2)
            print(tables[0])
            print(tables[1])
        except Exception as e:
            # if there is an error, print the information and continue to next test case
            print("ini_case2() raise custom error:", e.__class__.__name__)
            print("detail:", e)
            pass

    def test_ini_case3(self):
        path0 = "tests/data/small_network/input/input_network_data.json"
        path1 = "tests/data/small_network/input/meta_data.json"
        path2 = "tests/data/small_network/input/active_power_profile.parquet"
        path3 = "tests/data/small_network/input/reactive_power_profile.parquet"
        path4 = "tests/data/small_network/input/ev_active_power_profile.parquet"
        opt_tap_pos_inst = optimal_tap_position(path0, path2, path3)
        try:
            # call the class.function, if there is an error then record it
            criteria = "minimize_line_losses"
            optimal_tap_pos = opt_tap_pos_inst.find_optimal_tap_position(criteria)
            print("optimal tap position: ", optimal_tap_pos)
            criteria = "minimize_voltage_deviations"
            optimal_tap_pos = opt_tap_pos_inst.find_optimal_tap_position(criteria)
            print("optimal tap position: ", optimal_tap_pos)
            criteria = "wrong_criteria"
            optimal_tap_pos = opt_tap_pos_inst.find_optimal_tap_position(criteria)
            print("optimal tap positionL ", optimal_tap_pos)
        except Exception as e:
            # if there is an error, print the information and continue to next test case
            print("ini_case3() raise custom error:", e.__class__.__name__)
            print("detail:", e)
            pass

    def test_ini_case4(self):
        path0 = "tests/data/small_network/input/input_network_data.json"
        path1 = "tests/data/small_network/input/meta_data.json"
        path2 = "tests/data/small_network/input/active_power_profile.parquet"
        path3 = "tests/data/small_network/input/reactive_power_profile.parquet"
        path4 = "tests/data/small_network/input/ev_active_power_profile.parquet"
        n1 = n1_calculation(path0, path1, path2, path3)
        try:
            # call the class.function, if there is an error then record it
            print(n1.n1_calculate(18))
            print(n1.n1_calculate(17))
        except Exception as e:
            # if there is an error, print the information and continue to next test case
            print("ini_case4() raise custom error:", e.__class__.__name__)
            print("detail:", e)
            pass

    def test_ini_case5(self):
        path0 = "tests/data/small_network/input/input_network_data_wrong.json"
        path1 = "tests/data/small_network/input/meta_data.json"
        path2 = "tests/data/small_network/input/active_power_profile.parquet"
        path3 = "tests/data/small_network/input/reactive_power_profile.parquet"
        path4 = "tests/data/small_network/input/ev_active_power_profile.parquet"
        pss = input_data_validity_check(path0)
        try:
            # call the class.function, if there is an error then record it
            pss.check_grid(path1)
            pss.check_graph()
            pss.check_matching(path2, path3, path4)
            pss.check_ev_charging_profiles()
        except Exception as e:
            # if there is an error, print the information and continue to next test case
            print("ini_case5() raise custom error:", e.__class__.__name__)
            print("detail:", e)
            pass

    def test_ini_case6(self):
        path0 = "tests/data/small_network/input/input_network_data.json"
        path1 = "tests/data/small_network/input/meta_data_wrong.json"
        path2 = "tests/data/small_network/input/active_power_profile.parquet"
        path3 = "tests/data/small_network/input/reactive_power_profile.parquet"
        path4 = "tests/data/small_network/input/ev_active_power_profile.parquet"
        pss = input_data_validity_check(path0)
        try:
            # call the class.function, if there is an error then record it
            pss.check_grid(path1)
            pss.check_graph()
            pss.check_matching(path2, path3, path4)
            pss.check_ev_charging_profiles()
        except Exception as e:
            # if there is an error, print the information and continue to next test case
            print("ini_case6() raise custom error:", e.__class__.__name__)
            print("detail:", e)
            pass

    def test_ini_case7(self):
        path0 = "tests/data/small_network/input/input_network_data_wrong2.json"
        path1 = "tests/data/small_network/input/meta_data.json"
        path2 = "tests/data/small_network/input/active_power_profile.parquet"
        path3 = "tests/data/small_network/input/reactive_power_profile.parquet"
        path4 = "tests/data/small_network/input/ev_active_power_profile.parquet"
        pss = input_data_validity_check(path0)
        try:
            # call the class.function, if there is an error then record it
            pss.check_grid(path1)
            pss.check_graph()
            pss.check_matching(path2, path3, path4)
            pss.check_ev_charging_profiles()
        except Exception as e:
            # if there is an error, print the information and continue to next test case
            print("ini_case7() raise custom error:", e.__class__.__name__)
            print("detail:", e)
            pass


if __name__ == "__main__":
    unittest.main()
