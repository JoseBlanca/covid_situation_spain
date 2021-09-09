
from numpy.lib.function_base import digitize
import config

from datetime import timedelta

import numpy

import covid_data
import plot


def plot_age_distributions(plot_path, date_range=None):
    data_per_age_group = covid_data.get_frame(date_range=date_range).groupby(by=config.ORIG_AGE_GROUP_COL).sum()

    fig = plot.SharedXFigure(data_per_age_group.shape[1], fig_size=(6, 8))

    age_groups = data_per_age_group.index
    x_poss = numpy.arange(len(list(age_groups)))

    for idx, param in enumerate(config.ORIG_COUNT_COLS):
        cases_per_age_group = data_per_age_group.loc[age_groups, param]
        axes = fig.get_axes(idx)
        axes.bar(x_poss, cases_per_age_group)
        axes.set_ylabel(config.PLOT_PARAM_DESCRIPTIONS[param])

    plot.set_x_ticks(axes, x_poss, age_groups)
    fig.save_fig(plot_path)


if __name__ == '__main__':
    last_date = covid_data.get_last_date_in_dframe()
    one_week = timedelta(days=7)
    last_date = last_date - one_week
    one_moth = timedelta(days=30)
    date_range = (last_date - one_moth, last_date)

    plot_path = config.PLOT_DIR / 'plot_ages_recent.svg'
    plot_age_distributions(plot_path, date_range)
    
    plot_path = config.PLOT_DIR / 'plot_ages_all.svg'
    plot_age_distributions(plot_path)
