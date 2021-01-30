from datetime import date, datetime
import pickle
import time

from google_sheet_pandas_reader import connect_to_google_sheet


def get_metrics_analytics():
    # Request metrics and get feedback

    while True:
        metrics_df = connect_to_google_sheet()

        all_metrics = metrics_df["Metric name"]
        report_dict = dict()

        for metric in all_metrics:
            this_metric_df = metrics_df[metrics_df["Metric name"] == metric]
            metric_val = int(this_metric_df.Value)
            metric_min = int(this_metric_df.Lower_bound)
            metric_max = int(this_metric_df.Upper_bound)
            metric_dept = str(this_metric_df["Relevant department"].iloc[0])
            datestamp = date.today()

            if metric_val < metric_min:
                key_name = metric + " negative report"

                report_dict[key_name] = ["negative", metric_dept, metric, metric_min, metric_val, datestamp]
            elif metric_val >= metric_max:
                key_name = metric + " positive report"
                report_dict[key_name] = ["positive", metric_dept, metric, metric_max, metric_val, datestamp]
            else:
                pass

        print("\n\nNEW REPORT:\n{}\n*****\n".format(report_dict))

        with open("data", "wb") as pickle_file:
            pickle.dump(report_dict, pickle_file)
            print("file updated at {}".format(datetime.now()))

        time.sleep(3)


if __name__ == "__main__":
    print("\n\n*** Executing ***\n\n")
    get_metrics_analytics()
