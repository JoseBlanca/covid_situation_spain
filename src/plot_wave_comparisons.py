import config

from collections import defaultdict

import numpy

import covid_data
import plot


def plot_data_per_wave(plot_path, title, age_ranges=None):

    params_to_plot = [config.ORIG_HOSP_COL, config.ORIG_ICU_COL, config.ORIG_DEATHS_COL]

    totals = defaultdict(list)
    for date_range in config.WAVE_RANGES:
        dframe = covid_data.get_frame(date_range=date_range, age_ranges=age_ranges)
        total = dframe.sum()
        for data_kind in params_to_plot:
            totals[data_kind].append(total[data_kind])

    fig = plot.SharedXFigure(
        num_axes=len(params_to_plot),
        fig_size=config.THREE_PANEL_EVOLUTION_FIG_SIZE,
    )
    x_poss = None
    for idx, param in enumerate(params_to_plot):
        axes = fig.get_axes(idx)
        if x_poss is None:
            x_poss = numpy.arange(1, len(totals[param]) + 1)
            axes.set_title(title)
        axes.bar(x_poss, totals[param])
        axes.set_ylabel(config.PLOT_PARAM_DESCRIPTIONS[param])

    axes.set_xlabel("ola")

    fig.save_fig(plot_path)


if __name__ == "__main__":

    out_dir = config.PLOT_DIR
    out_dir.mkdir(exist_ok=True)

    plot_path = out_dir / f"waves.png"
    plot_data_per_wave(plot_path, title="Totales por ola")

    plot_path = out_dir / f"waves_children.png"
    plot_data_per_wave(
        plot_path,
        age_ranges=["0-9"],
        title="Totales por ola (Niños 0-9)",
    )
