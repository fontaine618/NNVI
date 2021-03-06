import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
plt.style.use("seaborn")

PATH = "/home/simon/Documents/NNVI/sims/"
EXPERIMENTS = [
    "covariate_binary",
    "covariate_continuous",
    "density_binary",
    "density_continuous",
    "missingrate_binary",
    "missingrate_continuous",
    "networksize_binary",
    "networksize_continuous"
]
BINARY = [True, False, ]*4
XAXIS = [
    "p_bin", "p_cts",
    "density", "density",
    "missing_rate", "missing_rate",
    "N", "N",
]
CURVES = [
    "N", "N",
    "p_bin", "p_cts",
    "p_bin", "p_cts",
    "p_bin", "p_cts",
]
ALGOS = ["VIMC", "ADVI", "MLE", "MICE"]
colors = {"MLE": "#4c72b0", "ADVI": "#55a868", "VIMC": "#c44e52", "MICE": "#8172b2"}
WHICH = [1000, 1000, 100, 100, 100, 100, 100, 100]

DICT = {"MLE": "MLE", "ADVI": "NAIVI-QB", "VIMC": "NAIVI-MC", "MICE": "MICE",
        "N": "Network size", "p_bin": "Nb. attributes", "p_cts": "Nb. covariates",
        "density": "Network density", "missing_rate": "Missing rate",
        "cts": "Continuous", "bin": "Binary"}

cov_type = "cts"
cov_type = "bin"

fig, axs = plt.subplots(2, 4, sharex="col", figsize=(5, 3), sharey="row")

for i, (exp, bin, xaxis, curves, which) in enumerate(zip(EXPERIMENTS, BINARY, XAXIS, CURVES, WHICH)):
    print(exp)
    if cov_type == "cts":
        j = i // 2
        if bin:
            continue
    else:
        j = (i+1) // 2
        if not bin:
            continue
    exp_short = exp.split("_")[0]
    yaxis = "test_auroc" if bin else "test_mse"
    file = PATH + exp + "/results/summary.csv"
    if os.path.isfile(file):
        results = pd.read_csv(file, index_col=0)
    else:
        print("---skipped (file not found)")
        continue
    algo = results["algo"]
    for a in ALGOS:
        df = results[algo == a]
        df = df[df[curves] == which]
        group = xaxis if xaxis != "density" else "alpha_mean"
        mean = df.groupby([group, curves]).agg("mean").reset_index()
        std = df.groupby([group, curves]).agg("std").reset_index()
        axs[0][j].plot(mean[xaxis], mean[yaxis], color=colors[a], label=DICT[a])
        axs[0][j].fill_between(mean[xaxis], mean[yaxis]-std[yaxis],
                               mean[yaxis]+std[yaxis], color=colors[a], alpha=0.2)
        if a != "MICE":
            axs[1][j].plot(mean[xaxis], mean["dist_inv"], color=colors[a])
            axs[1][j].fill_between(mean[xaxis], mean["dist_inv"]-std["dist_inv"],
                                   mean["dist_inv"]+std["dist_inv"], color=colors[a], alpha=0.2)
    if xaxis in ["N", "p_cts", "p_bin"]:
        axs[0][j].set_xscale("log")
    axs[0][j].set_title("Setting {}".format("ABCDEFG"[j]))
    axs[1][j].set_xlabel(DICT[xaxis])
    axs[1][j].set_ylim(0., 0.8)

# legend
lines = [Line2D([0], [0], color=colors[a]) for a in ALGOS]
labels = [DICT[a] for a in ALGOS]
fig.legend(lines, labels, loc=8, ncol=len(ALGOS)) #, title="Algorithm")
# ylabels
axs[0][0].set_ylabel("MSE" if cov_type == "cts" else "AUROC")
axs[1][0].set_ylabel("$D(\widehat Z, Z)$")
axs[0][0].get_yaxis().set_label_coords(-0.4, 0.5)
axs[1][0].get_yaxis().set_label_coords(-0.4, 0.5)
# layout
fig.tight_layout(h_pad=0.5, w_pad=0.)
fig.subplots_adjust(bottom=0.30)

fig.savefig(PATH + "figs/{}_results.pdf".format(cov_type))