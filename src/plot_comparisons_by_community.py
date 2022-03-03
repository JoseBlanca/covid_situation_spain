import config

from datetime import timedelta, datetime

import numpy

import covid_data
import plot
import spain_data


def plot_region_comparison(
    plot_path, dframes_per_param, title, region_type, params_to_plot, is_absolute
):

    fig = plot.SharedXFigure(
        num_axes=len(params_to_plot),
        fig_size=config.THREE_PANEL_EVOLUTION_FIG_SIZE,
    )

    x_poss = None
    for idx, param in enumerate(params_to_plot):
        region_values = dframes_per_param[param].sum(axis=0)

        if x_poss is None:
            x_poss = numpy.arange(region_values.size)

        axes = fig.get_axes(idx)
        axes.bar(x_poss, region_values)

        ylabel = config.PLOT_PARAM_DESCRIPTIONS[param]
        if not is_absolute:
            ylabel = f"{ylabel} (por 1e5 hab.)"
        else:
            ylabel = f"{ylabel}"
        plot.set_y_label(axes, ylabel)

    if region_type == config.COMMUNITY:
        names_for_regions = spain_data.CA_NAMES_PER_ISO_CODE
    else:
        names_for_regions = spain_data.PROVINCE_NAMES_PER_ISO_CODE

    labels = [names_for_regions[region_iso] for region_iso in region_values.index]
    plot.set_x_ticks(fig.get_axes(len(params_to_plot) - 1), x_poss, labels)

    fig.get_axes(0).set_title(title)

    fig.save_fig(plot_path)


if __name__ == "__main__":

    last_date = covid_data.get_last_date_in_dframe()
    first_date = datetime(year=2021, month=11, day=1)
    date_range = (first_date, last_date)
    params_to_plot = [config.ORIG_HOSP_COL, config.ORIG_DEATHS_COL]

    out_dir = config.PLOT_DIR
    date_range_name = f"sexta_ola"
    date_range_title = f"sexta ola ({first_date.day}/{first_date.month}/{first_date.year}-{last_date.day}/{last_date.month}/{last_date.year})"
    by = config.COMMUNITY
    for kind in ("absolute", "relative"):
        plot_path = out_dir / f"community_comparison_{date_range_name}_{kind}.png"
        dframes_per_param = covid_data.get_evolutions_per_param(
            by=by, date_range=date_range, rate_by_100k=(kind == "relative")
        )
        if date_range is None:
            title = "Parámetros desde el inicio de la pandemia"
        else:
            num_weeks = int((date_range[1] - date_range[0]) / timedelta(weeks=1))
            first_date = date_range[0]
            last_date = date_range[1]
            title = f"{date_range_title}"

        plot_region_comparison(
            plot_path,
            dframes_per_param,
            title,
            region_type=by,
            params_to_plot=params_to_plot,
            is_absolute=(kind == "absolute"),
        )
