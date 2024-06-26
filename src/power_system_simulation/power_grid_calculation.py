"""
Assignment 2: Power Grid Calculation
"""

import warnings
from datetime import datetime

import numpy as np
import pandas as pd
from scipy import integrate

with warnings.catch_warnings(action="ignore", category=DeprecationWarning):
    # suppress warning about pyarrow as future required dependency
    from pandas import DataFrame

from power_grid_model import CalculationMethod, CalculationType, PowerGridModel, initialize_array
from power_grid_model.utils import json_deserialize
from power_grid_model.validation import assert_valid_batch_data, assert_valid_input_data


class TwoProfilesDoesNotHaveMatchingTimestampsOrLoadIds(Exception):
    """
    Exception to check if two load profiles do not have matching timestamps or load IDs.
    """


class PowerGridCalculation:
    """
    Class to perform power grid calculations.
    """

    def __init__(self) -> None:
        """
        Initialize the PowerGridCalculation class.
        """

    def construct_pgm(self, data_path: str):
        """
        Construct the Power Grid Model (PGM) from the provided JSON data.

        Args:
        data_path (str): Path to the JSON data file.

        Returns:
        dict: Deserialized dataset containing input data for PGM.
        """
        # open the file from certain path
        with open(data_path) as fp:
            data = fp.read()
        # read from jason
        self.dataset = json_deserialize(data)
        assert_valid_input_data(input_data=self.dataset, calculation_type=CalculationType.power_flow)
        return self.dataset

    def creat_batch_update_dataset(self, data_path1: str, data_path2: str):
        """
        1.  Create a PGM batch update dataset from the parquet files containing the active and reactive load profiles.
        2.  Raise error if timestamps and Load IDs don't match between active and reactive power load profiles.
        3.  Store the timestamps from the load profiles.
        4.  Create the format of load profile data for batch calculation.
        5.  Assign the attributes for the batch calculation:
            - Load IDs
            - Active power load
            - Reactive power load
        6.  Store and return the batch update dataset.

        Args:
        data_path1 (str): Path to the active power load profile parquet file.
        data_path2 (str): Path to the reactive power load profile parquet file.

        Returns:
        dict: Dictionary containing the batch update dataset.

        Raises:
        TwoProfilesDoesNotHaveMatchingTimestampsOrLoadIds.
        """
        # read from parquet
        df_load_profile1 = pd.read_parquet(data_path1)
        df_load_profile2 = pd.read_parquet(data_path2)
        # validate dataset
        if not np.all(df_load_profile1.columns == df_load_profile2.columns):
            raise TwoProfilesDoesNotHaveMatchingTimestampsOrLoadIds
        if not np.all(df_load_profile1.index == df_load_profile2.index):
            raise TwoProfilesDoesNotHaveMatchingTimestampsOrLoadIds
        # store time stamp info
        self.timestamp = df_load_profile1.index
        # create format
        load_profile = initialize_array("update", "sym_load", df_load_profile1.shape)
        # Set the attributes for the batch calculation
        load_profile["id"] = df_load_profile1.columns.to_numpy()
        load_profile["p_specified"] = df_load_profile1.to_numpy()
        load_profile["q_specified"] = df_load_profile2.to_numpy()
        # store dataset
        self.update_data = {"sym_load": load_profile}
        # return the dataset if needed
        return self.update_data

    def time_series_power_flow_calculation(self):
        """
        Perform time series power flow calculation for every timestep in the dataset.

        1.  Validate the input & update data.
        2.  Create a PowerGridModel instance using validated input data.
        3.  Perform power flow calculation using the Newton-Raphson method for each timestep of the dataset,
            and store the results.
        4.  Create a dataframe for both the node and line results at each timestep.
        5.  Store the following results for each timestep:
            - Node results: Maximum and minimum voltage magnitudes and corresponding node IDs.
            - Line results: Maximum and minimum loading and corresponding timestamps, and energy loss.
        6.  Return results in a list of 2 tables: Node results and Line results.

        Args:
        None

        Returns:
        list: List of 2 tables containing node and line results for each timestep.

        Raises:
        AssertionError: If the input or update data is invalid.
        """
        # validate
        assert_valid_batch_data(
            input_data=self.dataset, update_data=self.update_data, calculation_type=CalculationType.power_flow
        )
        # create model
        model = PowerGridModel(input_data=self.dataset)
        output_data = model.calculate_power_flow(
            update_data=self.update_data, calculation_method=CalculationMethod.newton_raphson
        )
        # table for nodes
        table1 = pd.DataFrame()
        table1["Timestamp"] = self.timestamp
        table1.set_index("Timestamp")
        table1["max_id"] = 0
        table1["max_pu"] = 0.0
        table1["min_id"] = 0
        table1["min_pu"] = 0.0
        i = 0
        for node_scenario in output_data["node"]:
            df = pd.DataFrame(node_scenario)
            max_value_id = df.at[df["u_pu"].idxmax(), "id"]
            min_value_id = df.at[df["u_pu"].idxmin(), "id"]
            max_value_pu = df.at[df["u_pu"].idxmax(), "u_pu"]
            min_value_pu = df.at[df["u_pu"].idxmin(), "u_pu"]
            table1.loc[i, "max_id"] = max_value_id
            table1.loc[i, "max_pu"] = max_value_pu
            table1.loc[i, "min_id"] = min_value_id
            table1.loc[i, "min_pu"] = min_value_pu
            i = i + 1
        # table for lines
        table2 = pd.DataFrame()
        table2["Line_ID"] = output_data["line"]["id"][0]
        table2.set_index("Line_ID")
        table2["max_time"] = datetime.fromtimestamp(0)
        table2["max__loading_pu"] = 0.0
        table2["min_time"] = datetime.fromtimestamp(0)
        table2["min_loading_pu"] = 0.0
        table2["energy_loss_kw"] = 0.0
        df_temp = pd.DataFrame()
        df_temp = pd.DataFrame(output_data["line"]["loading"])
        df_temp["Timestamp"] = self.timestamp
        i = 0
        for column_name, column_data in df_temp.iloc[:, :-1].items():
            table2.loc[i, "max__loading_pu"] = column_data.max()
            table2.loc[i, "max_time"] = df_temp["Timestamp"][column_data.idxmax()]
            table2.loc[i, "min_loading_pu"] = column_data.min()
            table2.loc[i, "min_time"] = df_temp["Timestamp"][column_data.idxmin()]
            i = i + 1
        # p_loss
        p_loss = pd.DataFrame()
        p_loss = pd.DataFrame(output_data["line"]["p_from"]) + pd.DataFrame(output_data["line"]["p_to"])
        i = 0
        for column_name, column_data in p_loss.items():
            table2.loc[i, "energy_loss_kw"] = integrate.trapezoid(column_data.to_list()) / 1000
            i = i + 1
        # return
        tables = [table1, table2]
        return tables

    def set_update_data(self, update_data):
        """
        Update the internal update_data dictionary.
        """
        self.update_data = update_data
