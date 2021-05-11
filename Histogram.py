import json

import pandas as pd
import matplotlib.pyplot as plt


class Histogram:
    def __init__(
        self,
        primary_grouping_column,
        value_column,
        df,
    ):
        self._max_groupings = 5
        self._primary_grouping_column = primary_grouping_column
        self._value_column = value_column
        self._aggregation = "sum"
        self._chart_type = "bar"
        self._input_df = df
        plt.clf()
        plt.style.use("seaborn")

    def set_max_groupings(self, max_groupings):
        assert max_groupings >= 0, "max_groupings must be greater or equal to zero"
        self._max_groupings = max_groupings

    def set_aggregation(self, aggregation):
        possible_values = ["sum", "count", "unique_count", "avg"]
        assert (
            aggregation in possible_values
        ), f"aggregation must be one of: {possible_values}"
        self._aggregation = aggregation

    def set_chart_type(self, chart_type):
        possible_values = ["bar", "barh"]
        assert (
            chart_type in possible_values
        ), f"chart_type must be one of: {possible_values}"
        self._chart_type = chart_type

    def _group_data(self):
        if self._aggregation == "unique_count":
            return self._group_data_unique_count()
        prepped_df = self._input_df
        if self._max_groupings != 0:
            prepped_df = self._filter_to_largest_groupings()

        if self._aggregation == "sum":
            new_group = prepped_df.groupby(
                [
                    self._primary_grouping_column,
                ]
            )[self._value_column].sum()
        if self._aggregation == "count":
            new_group = prepped_df.groupby(
                [
                    self._primary_grouping_column,
                ]
            )[self._value_column].count()
        ascending = False
        if self._chart_type == "barh":
            ascending = True
        new_group = new_group.sort_values(ascending=ascending)
        return new_group

    def _group_data_unique_count(self):
        new_group = self._input_df.groupby(
            [
                self._primary_grouping_column,
            ]
        ).agg({self._value_column: "nunique"})
        largest_df = (
            new_group[self._value_column].nlargest(self._max_groupings).to_frame()
        )
        largest_categories = largest_df.index.values.tolist()
        filtered_to_largest = new_group[new_group.index.isin(largest_categories)]
        ascending_option = False
        if self._chart_type == "barh":
            ascending_option = True
        filtered_to_largest = filtered_to_largest.sort_values(
            by=self._value_column, ascending=ascending_option
        )
        return filtered_to_largest

    def _filter_to_largest_groupings(self):
        if self._aggregation == "sum":
            largest_df = (
                self._input_df.groupby([self._primary_grouping_column])[
                    self._value_column
                ]
                .sum()
                .nlargest(self._max_groupings)
                .to_frame()
            )
        else:
            largest_df = (
                self._input_df.groupby([self._primary_grouping_column])[
                    self._value_column
                ]
                .count()
                .nlargest(self._max_groupings)
                .to_frame()
            )
        largest_categories = largest_df.index.values.tolist()
        filtered_to_largest = self._input_df[
            self._input_df[self._primary_grouping_column].isin(largest_categories)
        ]
        return filtered_to_largest

    def to_json(self):
        self._grouped_df = self._group_data()
        json_str = self._grouped_df.to_json()
        json_dict = json.loads(json_str)
        return json_dict

    def save_plot(self, filename):
        self._grouped_df = self._group_data()
        self._grouped_df.plot(kind=self._chart_type)
        plt.tight_layout()
        plt.savefig(filename)
