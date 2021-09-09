
import config

from datetime import timedelta, datetime

import covid_data
import plot
import spain_data

AGE_GROUPS = {'0-9': ['0-9'],
              '10-19': ['10-19'],
              '20-39': ['20-29', '30-39'],
              '40-59': ['40-49', '50-59'],
              '60-69': ['60-69'],
              '70+': ['70-79', '80+']}

AGE_GROUP_COLORS = {'0-9': '#FF69B4',
                    '10-19': '#BA55D3',
                    '20-39': '#00BFFF',
                    '40-59': '#228B22',
                    '60-69': '#778899',
                    '70+': '#000000'}


def _calculate_relative_to_cases(evolutions):
    num_cases = evolutions[config.ORIG_CASES_COL].values
    evolutions = evolutions.div(num_cases, axis='index')
    del evolutions[config.ORIG_CASES_COL]
    return evolutions

def plot_age_evolution(plot_path, sex=None, date_range=None,
                       rate_by_100k=False, by_week=False,
                       age_ranges=None,
                       community=None, title=None):

    params_to_plot = config.ORIG_COUNT_COLS

    fig = plot.SharedXFigure(num_axes=len(params_to_plot),
                             fig_size=config.FOR_PANEL_EVOLUTION_FIG_SIZE)

    for idx, (age_group_name, ages) in enumerate(age_ranges.items()):
        if community is None:
            evolutions = covid_data.get_evolutions_for_spain(sex=sex,
                                                             date_range=date_range,
                                                             rate_by_100k=rate_by_100k,
                                                             by_week=by_week,
                                                             age_ranges=ages)
        else:
            evolutions = covid_data.get_evolutions_per_param(by=config.COMMUNITY, sex=sex, date_range=date_range,
                                                             rate_by_100k=rate_by_100k, by_week=by_week,
                                                             age_ranges=ages)
            evolutions = {param: evolution.loc[:, community] for param, evolution in evolutions.items()}

        res = _plot_evolution_for_age_group(fig, evolutions, rate_by_100k,
                                            age_group_name, by_week, date_range,
                                            params_to_plot)

    axes = fig.get_axes(0)
    axes.legend()

    if title:
        axes.set_title(title)

    fig.save_fig(plot_path)


def _plot_evolution_for_age_group(fig, evolutions, rate_by_100k, age_group_name, by_week, date_range, params_to_plot):
    for idx, param in enumerate(params_to_plot):
        axes = fig.get_axes(idx)
        evolution = evolutions[param]
        if date_range is not None:
            evolution = evolution.loc[date_range[0]: date_range[1]]
        axes.plot(evolution.index, evolution.values,
                  color=AGE_GROUP_COLORS[age_group_name],
                  label=age_group_name)

        ylabel = config.PLOT_PARAM_DESCRIPTIONS[param]
        if rate_by_100k:
            ylabel = f'{ylabel} (por 1e5 hab.)'
        if by_week:
            ylabel = f'{ylabel}\n(semanal)'
        plot.set_y_label(axes, ylabel)
        plot.set_x_ticks_format(axes, 45, ha='right')
    return {'axes': axes}



if __name__ == '__main__':

    last_date = covid_data.get_last_date_in_dframe()
    one_week = timedelta(days=7)
    last_date = last_date - one_week
    first_date = datetime(2021, 3, 1)
    DATE_RANGE = (first_date, last_date)

    date_rage_str = f'{first_date.date().day}-{first_date.date().month} al {last_date.date().day}-{last_date.date().month}'

    out_dir = config.AGE_COMMUNITY_GROUP_PLOT_DIR
    out_dir.mkdir(exist_ok=True)

    region_names_per_iso_code = spain_data.CA_NAMES_PER_ISO_CODE
    for region_iso, region_name in region_names_per_iso_code.items():
        if region_iso == 'nd':
            continue
        plot_path = out_dir / f'evolution_per_age_range.{region_name}.{date_rage_str}.svg'
        plot_age_evolution(plot_path, by_week=True, date_range=DATE_RANGE,
                                     age_ranges=AGE_GROUPS, rate_by_100k=True,
                                     community=region_iso, title=region_name)

        plot_path = out_dir / f'evolution_per_age_range.{region_name}.svg'
        plot_age_evolution(plot_path, by_week=True, date_range=None,
                                     age_ranges=AGE_GROUPS, rate_by_100k=True,
                                     community=region_iso, title=region_name)

    out_dir = config.AGE_GROUP_PLOT_DIR
    out_dir.mkdir(exist_ok=True)

    plot_path = out_dir / f'evolution_per_age_range.{date_rage_str}.svg'
    plot_age_evolution(plot_path, by_week=True, date_range=DATE_RANGE,
                       age_ranges=AGE_GROUPS, rate_by_100k=True)


    plot_path = out_dir / 'evolution_per_age_range.svg'
    plot_age_evolution(plot_path, by_week=True, date_range=None,
                       age_ranges=AGE_GROUPS, rate_by_100k=True)

