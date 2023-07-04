import numpy as np
from auditok.plotting import _plot_line, _plot_detections, _make_time_axis
from matplotlib import pyplot as plt

CUSTOM_PLOT_THEME = {
    "figure": {"facecolor": "#482a36", "alpha": 0.},
    "plot": {"facecolor": "#282a36", "alpha": 1.},
    "energy_threshold": {
        "color": "#e31f8f",
        "linestyle": "--",
        "linewidth": 1,
    },
    "signal": {"color": "#40d970", "linestyle": "-", "linewidth": 1},
    "detections": {
        "facecolor": "#777777",
        "edgecolor": "#ff8c1a",
        "linewidth": 1,
        "alpha": 0.75,
    },
}


def auditok_custom_plot(
        audio_region,
        scale_signal=True,
        detections=None,
        energy_threshold=None,
        show=False,
        figsize=None,
        save_as=None,
        dpi=120,
        theme="auditok",
):
    y = np.asarray(audio_region)
    if len(y.shape) == 1:
        y = y.reshape(1, -1)
    nb_subplots, nb_samples = y.shape
    sampling_rate = audio_region.sampling_rate
    time_axis = _make_time_axis(nb_samples, sampling_rate)
    if energy_threshold is not None:
        eth_log10 = energy_threshold * np.log(10) / 10
        amplitude_threshold = np.sqrt(np.exp(eth_log10))
    else:
        amplitude_threshold = None
    if detections is None:
        detections = []
    else:
        # End of detection corresponds to the end of the last sample but
        # to stay compatible with the time axis of signal plotting we want end
        # of detection to correspond to the *start* of the that last sample.
        detections = [
            (start, end - (1 / sampling_rate)) for (start, end) in detections
        ]
    if theme == "auditok":
        theme = CUSTOM_PLOT_THEME

    fig = plt.figure(figsize=figsize, dpi=dpi)
    fig_theme = theme.get("figure", theme.get("fig", {}))
    fig_fc = fig_theme.get("facecolor", fig_theme.get("ffc"))
    fig_alpha = fig_theme.get("alpha", 1)
    fig.patch.set_facecolor(fig_fc)

    fig.patch.set_alpha(fig_alpha)

    plot_theme = theme.get("plot", {})
    plot_fc = plot_theme.get("facecolor", plot_theme.get("pfc"))

    if nb_subplots > 2 and nb_subplots % 2 == 0:
        nb_rows = nb_subplots // 2
        nb_columns = 2
    else:
        nb_rows = nb_subplots
        nb_columns = 1

    for sid, samples in enumerate(y, 1):
        ax = fig.add_subplot(nb_rows, nb_columns, sid)
        ax.set_facecolor(plot_fc)
        if scale_signal:
            std = samples.std()
            if std > 0:
                mean = samples.mean()
                std = samples.std()
                samples = (samples - mean) / std
                max_ = samples.max()
                plt.ylim(-1.5 * max_, 1.5 * max_)
                plt.xlim(time_axis[0], time_axis[-1])
        if amplitude_threshold is not None:
            if scale_signal and std > 0:
                amp_th = (amplitude_threshold - mean) / std
            else:
                amp_th = amplitude_threshold
            eth_theme = theme.get("energy_threshold", theme.get("eth", {}))
            _plot_line(
                [time_axis[0], time_axis[-1]],
                [amp_th] * 2,
                eth_theme
            )

        signal_theme = theme.get("signal", {})
        _plot_line(
            time_axis,
            samples,
            signal_theme,
        )
        detections_theme = theme.get("detections", {})
        _plot_detections(ax, detections, detections_theme)
        ax.set_xticks([])
        ax.set_yticks([])

    fig.tight_layout(pad=0)

    if save_as is not None:
        plt.savefig(save_as, dpi=dpi)
    if show:
        plt.show()
