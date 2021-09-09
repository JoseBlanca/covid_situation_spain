
import config

from datetime import timedelta

import numpy

import covid_data
import plot
import demography
import spain_data


def _age_group_first_num(age_group):
    first =age_group.split('-')[0].strip('+')
    if first == 'NC':
        age = 1000
    else:
        age = int(first)
    return age


def plot_params_per_age_group(plot_path, sex=None, date_range=None):
    dframe = covid_data.get_frame(sex=sex, date_range=date_range)
    values_per_age_group = dframe.groupby(by=config.ORIG_AGE_GROUP_COL).sum()

    fig = plot.SharedXFigure(num_axes=values_per_age_group.shape[1])

    age_groups = None
    for idx, param in enumerate(config.ORIG_COUNT_COLS):
        values = values_per_age_group[param]

        if age_groups is None:
            age_groups = sorted(values.index, key=_age_group_first_num)
            xposs = numpy.arange(len(age_groups))
        print(age_groups)

        values = values.loc[age_groups]

        axes = fig.get_axes(idx)
        axes.bar(xposs, values)
        plot.set_y_label(axes, config.PLOT_PARAM_DESCRIPTIONS[param])
        plot.set_x_ticks(axes, xposs, age_groups)

    fig.save_fig(plot_path)


def get_proportion_dead(age_groups=None, date_range=None, param=config.ORIG_DEATHS_COL):
    dframe = covid_data.get_frame(date_range=date_range)
    ccaa = [spain_data.CA_PER_PROVINCE.get(province_iso, 'nd') for province_iso in dframe[config.ORIG_PROVINCE_COL]]
    values_per_age_group = dframe.groupby(by=[config.ORIG_AGE_GROUP_COL, ccaa]).sum()
    values_per_age_group.index.names = (config.ORIG_AGE_GROUP_COL, 'ca')
    values_per_ca = values_per_age_group[param].groupby(['ca']).sum()

    values = values_per_age_group[param]
    if age_groups is None:
        age_groups = sorted(values.index, key=_age_group_first_num)
    values = values.loc[age_groups]

    num_people = demography.get_demographic_data_by_community(age_ranges=age_groups)

    one_out_of = num_people / values_per_ca
    return one_out_of


if __name__ == '__main__':
    one_out_of = get_proportion_dead(age_groups=['80+'])
    print('Fallecidos mayores de 80 años (1 de cada)')
    for ca_iso, number in one_out_of.sort_values().iteritems():
        print(spain_data.CA_NAMES_PER_ISO_CODE[ca_iso], number)

    plot_path = config.AGE_GROUP_PLOT_DIR / 'params_per_age_group.svg'
    plot_params_per_age_group(plot_path)

    last_date = covid_data.get_last_date_in_dframe()
    one_week = timedelta(days=7)
    last_date = last_date - one_week
    first_date = last_date - timedelta(days=7)
    date_range = (first_date, last_date)

    date_rage_str = f'{first_date.date().day}-{first_date.date().month} al {last_date.date().day}-{last_date.date().month}'

    plot_path = config.AGE_GROUP_PLOT_DIR / f'params_per_age_group-{date_rage_str}.svg'
    plot_params_per_age_group(plot_path, date_range=date_range)
