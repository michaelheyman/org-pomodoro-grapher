from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

FIGURE_WIDTH = 12
FIGURE_HEIGHT = 12


def parse_pomodoro_line(line):
    date = line[1]
    date = date[1:]

    duration = line[-1]
    mins, secs = duration.split(":")
    total_seconds = int(mins) * 60 + int(secs)

    return date, total_seconds


def run():
    filename = "tasks-example.org"

    with open(filename, "r") as file:
        min_date = datetime.now().date()
        max_date = 0
        terms = dict()
        current_term_name = (
            ""
        )  # variable set for local access inside course if-statement
        current_course_name = ""

        for file_line in file:
            line = file_line.split()

            if "*" in line[0]:
                if len(line[0]) == 1:  # term
                    current_term_name = line[1]
                    terms[current_term_name] = {}

                if len(line[0]) == 2:  # course
                    current_course_name = " ".join(line[1:])
                    terms[current_term_name].update({current_course_name: {}})

                # if len(line[0]) is 3:  # task
                #    task_name = " ".join(line[1:])

            if line[0] == "CLOCK:":  # pomodoro line
                date, seconds = parse_pomodoro_line(line)
                if date < str(min_date):
                    min_date = date
                if date > str(max_date):
                    max_date = date

                seconds = seconds / 60.0  # set seconds to hours

                if date in terms[current_term_name][current_course_name].keys():
                    terms[current_term_name][current_course_name][date] += seconds
                else:
                    terms[current_term_name][current_course_name].update(
                        {date: seconds}
                    )

    plot_all_courses(terms)


def plot_all_courses(terms):
    for term, courses in terms.items():
        plot_courses(courses, term)


def plot_courses(courses, term):
    daily_activity_df = create_dataframe(courses)
    cumulative_activity_df = create_total_minutes_dataframe(daily_activity_df)

    # create array of subplots and figure
    fig, axes = plt.subplots(nrows=2, ncols=1)

    plot_cumulative_activity(axes, cumulative_activity_df, term)
    plot_daily_activity(axes, daily_activity_df, term)

    # display plots
    fig.savefig(term)  # to file
    plt.show()  # on screen


def plot_daily_activity(axes, df, term):
    daily_activity_plot = df.plot.bar(
        ax=axes[1],
        title=term,
        figsize=(FIGURE_WIDTH, FIGURE_HEIGHT),
        rot=90,
        stacked=True,
    )
    daily_activity_plot.set_ylabel("Hours")

    xticklabels = [
        remove_timestamp(label) for label in daily_activity_plot.get_xticklabels()
    ]

    daily_activity_plot.set_xticklabels(xticklabels, visible=False)

    # display every 7th tick label, to match area plot format
    for tick in daily_activity_plot.xaxis.get_ticklabels()[::2]:
        tick.set_visible(True)

    daily_activity_plot.axhline(
        average_time_per_day(df), color="b", alpha=0.2, ls="dashed"
    )
    # adjust horizontal space between subplots
    plt.subplots_adjust(hspace=0.3)


def remove_timestamp(label):
    return datetime.strptime(label.get_text(), "%Y-%m-%d %H:%M:%S").strftime("%b-%d")


def average_time_per_day(dataframe):
    return dataframe.values.sum() / len(dataframe.index)


def plot_cumulative_activity(axes, df2, term):
    total_minutes_plot = df2.plot.area(
        ax=axes[0], title=term, figsize=(FIGURE_WIDTH, FIGURE_HEIGHT)
    )
    total_minutes_plot.set_ylabel("Total Hours")
    total_minutes_plot.set_xlim(
        df2.index.min(), df2.index.max()
    )  # sets data plotting to origin


def create_total_minutes_dataframe(df):
    """ Create DataFrame to plot total minutes plot """

    columns_dict = {}
    for column_name in df.columns:
        columns_dict.update({column_name: df[column_name]})

    total_minutes_df = pd.DataFrame(columns_dict)
    total_minutes_df.cumsum()
    return total_minutes_df.cumsum()


def create_dataframe(courses):
    """ Create and sanitize DataFrame structure """

    df = pd.DataFrame.from_dict(courses)  # populate dataframe with courses dictionary
    df = df.fillna(0)  # fills 'NaN' with zeros
    df.index = pd.DatetimeIndex(df.index)  # prevents index from being overwritten
    df = df.reindex(
        pd.date_range(df.index.min().date(), df.index.max().date()), fill_value=0
    )  # reindexes
    return df


if __name__ == "__main__":
    run()
