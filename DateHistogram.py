import json

import pandas as pd
import matplotlib.pyplot as plt


class DateHistogram:
    def __init__(
        self,
        date_column_name,
        value_column,
        df,
    ):
        self._max_groupings = 5
        self._date_column_name = date_column_name
        self._date_period_name = date_column_name
        self._value_column = value_column
        self._aggregation = "sum"
        self._chart_type = "area"
        self._input_df = df
        plt.style.use("seaborn")

        # plt.show()

    def set_aggregation(self, aggregation):
        possible_values = ["sum", "count", "unique_count"]
        assert (
            aggregation in possible_values
        ), f"aggregation must be one of: {possible_values}"
        self._aggregation = aggregation

    def set_chart_type(self, chart_type):
        possible_values = ["area", "bar"]
        assert (
            chart_type in possible_values
        ), f"chart_type must be one of: {possible_values}"
        self._chart_type = chart_type

    def set_date_period(self, date_format, period):
        self._input_df["new_date"] = pd.to_datetime(
            self._input_df[self._date_column_name], format=date_format
        ).dt.to_period(period)
        self._date_period_name = "new_date"

    def _group_data(self):
        if self._aggregation == "sum":
            new_group = self._input_df.groupby([self._date_period_name])[
                self._value_column
            ].sum()

        if self._aggregation == "count":
            new_group = self._input_df.groupby([self._date_period_name])[
                self._value_column
            ].count()

        if self._aggregation == "unique_count":
            new_group = self._input_df.groupby([self._date_period_name])[
                self._value_column
            ].nunique()
        return new_group

    def to_json(self):
        self._grouped_df = self._group_data()
        json_str = self._grouped_df.to_json()
        json_dict = json.loads(json_str)
        return json_dict

    def save_plot(self, filename):
        fig, ax = plt.subplots()
        self._grouped_df = self._group_data()
        if self._chart_type == "bar":
            self._grouped_df.plot(kind=self._chart_type, stacked=True, width=0.8, ax=ax)
        else:
            self._grouped_df.plot(kind=self._chart_type, stacked=True, ax=ax)
        plt.xticks(rotation=90)
        legend = plt.legend(frameon=1)
        frame = legend.get_frame()
        frame.set_facecolor("white")
        plt.tight_layout()
        plt.savefig(filename)
