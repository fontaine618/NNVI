import pandas as pd
from pypet import Trajectory
import matplotlib.pyplot as plt
plt.style.use("seaborn")

# path
SIM_NAME = "missing_rate_binary"
SIM_PATH = "/home/simon/Documents/NNVI/simulations/" + SIM_NAME
RES_FILE = SIM_PATH + "/results/" + SIM_NAME + ".hdf5"

# load pypet trajectory
traj = Trajectory(SIM_NAME, add_time=False)
traj.f_load(
    filename=RES_FILE,
    load_data=2,
    load_results=2,
    load_derived_parameters=2,
    load_other_data=2,
    load_parameters=2,
    force=True
)
traj.v_auto_load = True

# load results
seed = [r.f_get("seed").seed for r in traj.res.runs]
p_bin = [r.f_get("p_bin").p_bin for r in traj.res.runs]
missing_rate = [r.f_get("missing_rate").missing_rate for r in traj.res.runs]

mse = [r.f_get("mse").mse for r in traj.res.runs]
elbo = [r.f_get("elbo").elbo for r in traj.res.runs]
auroc = [r.f_get("auroc").auroc for r in traj.res.runs]
dist_proj = [r.f_get("dist_proj").dist_proj for r in traj.res.runs]
dist_inv = [r.f_get("dist_inv").dist_inv for r in traj.res.runs]
density = [r.f_get("density").density for r in traj.res.runs]

# into df
results = pd.DataFrame({
    "missing_rate": missing_rate,
    "p_bin": p_bin,
    "seed": seed,
    "elbo": elbo,
    "mse": mse,
    "auroc": auroc,
    "dist_proj": dist_proj,
    "dist_inv": dist_inv,
    "density": density
})
results.to_csv(SIM_PATH + "/results/summary.csv", index=False)


results = pd.read_csv(SIM_PATH + "/results/summary.csv")

# drop stuff
results.dropna(inplace=True, how="any", axis=0)
results.drop(columns=["seed"], inplace=True)

# aggregate
stat = results.groupby(["p_bin", "missing_rate"]).agg(["mean", "std"])
n = results.groupby(["p_bin", "missing_rate"]).count()["elbo"]
stat["n"] = n

# statistics
names = {
    "auroc": "1 - AUROC",
    "dist_inv": "Distance to Z"
}

ns = {
    10: "darkred",
    100: "orangered",
    500: "darkorange"
}

# plot
fig, axs = plt.subplots(2, 1, figsize=(4, 6), sharex=True)

for i, (st, name) in enumerate(names.items()):
    ax = axs[i]
    for nn, col in ns.items():
        df = stat.loc[(nn, )]
        mean = df[(st, "mean")]
        std = df[(st, "std")]
        l = df["n"]
        ax.plot(df.index, mean, color=col, label=nn)
        ax.fill_between(df.index, mean-std, mean+std, color=col, alpha=0.2)
    if i==1:
        ax.set_xlabel("Missing rate")
    if i==0:
        ax.legend(loc="upper right", title="Nb. covariates")
    ax.set_ylabel(name)

fig.suptitle("Binary covariates")
fig.tight_layout()
fig.savefig(SIM_PATH + "/results/plot.pdf")

plt.close(fig)


# plot
fig, axs = plt.subplots(1, 1, figsize=(4, 4), sharex=True)

for i, (st, name) in enumerate(names.items()):
    ax = axs
    for nn, col in ns.items():
        df = stat.loc[(nn, )]
        mean = df[(st, "mean")]
        std = df[(st, "std")]
        l = df["n"]
        ax.plot(df.index, mean, color=col, label=nn)
        ax.fill_between(df.index, mean-std, mean+std, color=col, alpha=0.2)
        ax.set_xlabel("Missing rate")
        ax.legend(loc="upper right", title="Nb. covariates")
        ax.set_ylabel(name)
    break

fig.suptitle("Binary covariates")
fig.tight_layout()
fig.savefig(SIM_PATH + "/results/" + SIM_NAME + "_metric.pdf")

plt.close(fig)
