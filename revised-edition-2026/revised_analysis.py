"""
Revised analysis (2026) for the EDHEC BBA thesis
"Financial market & oil volatility within distressed economies:
wavelet coherence evidence from the early 21st century" (Yann Simons, 2022).

Same data as the 2022 thesis: monthly WTI, EPU and GPR, January 2000 - March 2022.
Outputs: figures (fig/), LaTeX tables (tab/) and key numbers (results.json).

Run:  python revised_analysis.py  [path/to/thesis_dataset_with_returns.csv]
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pycwt
import statsmodels.api as sm
from arch.unitroot import ADF, KPSS, PhillipsPerron
from scipy import stats
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import grangercausalitytests

HERE = Path(__file__).resolve().parent
DATA = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / "data" / "thesis_dataset_with_returns.csv"
FIG, TAB = HERE / "fig", HERE / "tab"
FIG.mkdir(exist_ok=True)
TAB.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "serif", "font.size": 9, "axes.spines.top": False,
                     "axes.spines.right": False, "savefig.bbox": "tight", "savefig.dpi": 200})
R = {}  # key numbers for the text
np.random.seed(20220719)  # Monte Carlo significance of the wavelet coherence

# --------------------------------------------------------------------------- data
df = pd.read_csv(DATA)
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date").asfreq("MS")
for c in ["WTI", "EPU", "GPR"]:
    df["d" + c] = np.log(df[c]).diff()          # log changes (revised specification)
d = df.dropna()
R["n_levels"], R["n_changes"] = len(df), len(d)
R["sample"] = [df.index.min().strftime("%B %Y"), df.index.max().strftime("%B %Y")]

# Figure 1: series
fig, ax = plt.subplots(3, 1, figsize=(6.3, 5.2), sharex=True)
for a, c, lab in zip(ax, ["WTI", "EPU", "GPR"],
                     ["WTI (US$ per barrel)", "EPU index", "GPR index"]):
    a.plot(df.index, df[c], lw=0.9, color="k")
    a.set_ylabel(lab)
    for s, e in [("2001-09", "2001-12"), ("2008-09", "2009-06"), ("2014-07", "2016-02"),
                 ("2020-02", "2020-12"), ("2022-02", "2022-03")]:
        a.axvspan(pd.Timestamp(s), pd.Timestamp(e), color="0.85", lw=0)
fig.align_ylabels()
fig.savefig(FIG / "fig1_series.pdf")
plt.close(fig)

# --------------------------------------------------------------------------- Table 1
def describe(s):
    jb = stats.jarque_bera(s.dropna())
    return [s.mean(), s.median(), s.std(), s.min(), s.max(), stats.skew(s.dropna()),
            stats.kurtosis(s.dropna(), fisher=False), jb.statistic, jb.pvalue]

cols = {"WTI": df["WTI"], "EPU": df["EPU"], "GPR": df["GPR"],
        r"$\Delta\ln$WTI": d["dWTI"], r"$\Delta\ln$EPU": d["dEPU"], r"$\Delta\ln$GPR": d["dGPR"]}
t1 = pd.DataFrame({k: describe(v) for k, v in cols.items()},
                  index=["Mean", "Median", "Std. dev.", "Min", "Max", "Skewness", "Kurtosis",
                         "Jarque-Bera", "JB p-value"])
R["jb"] = {k: float(t1.loc["Jarque-Bera", k]) for k in t1.columns}
R["kurt"] = {k: float(t1.loc["Kurtosis", k]) for k in t1.columns}
R["skew"] = {k: float(t1.loc["Skewness", k]) for k in t1.columns}


def fmt(x, nd=2):
    if abs(x) >= 1000:
        return f"{x:,.0f}"
    if x != 0 and abs(x) < 0.01:
        return f"{x:.4f}" if abs(x) >= 1e-4 else "<0.0001"
    return f"{x:.{nd}f}"


with open(TAB / "tab1_descriptive.tex", "w") as f:
    f.write("\\begin{tabular}{l" + "r" * 6 + "}\n\\toprule\n & " + " & ".join(t1.columns) +
            " \\\\\n\\midrule\n")
    for i, row in t1.iterrows():
        vals = [("<0.001" if (i == "JB p-value" and v < 0.001) else fmt(v, 3 if i != "Jarque-Bera" else 1))
                for v in row]
        f.write(f"{i} & " + " & ".join(vals) + " \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")

# --------------------------------------------------------------------------- Table 2: unit roots
rows = []
R["unitroot"] = {}
for name, s in [("ln WTI", np.log(df["WTI"])), ("ln EPU", np.log(df["EPU"])), ("ln GPR", np.log(df["GPR"])),
                ("Dln WTI", d["dWTI"]), ("Dln EPU", d["dEPU"]), ("Dln GPR", d["dGPR"])]:
    adf, pp, kp = ADF(s, trend="c", method="aic"), PhillipsPerron(s, trend="c"), KPSS(s, trend="c")
    rows.append([name, adf.stat, adf.pvalue, pp.stat, pp.pvalue, kp.stat, kp.pvalue])
    R["unitroot"][name] = {"adf_p": float(adf.pvalue), "pp_p": float(pp.pvalue), "kpss_p": float(kp.pvalue)}
lab = {"ln WTI": r"$\ln$ WTI", "ln EPU": r"$\ln$ EPU", "ln GPR": r"$\ln$ GPR",
       "Dln WTI": r"$\Delta\ln$ WTI", "Dln EPU": r"$\Delta\ln$ EPU", "Dln GPR": r"$\Delta\ln$ GPR"}
with open(TAB / "tab2_unitroot.tex", "w") as f:
    f.write("\\begin{tabular}{lrrrrrr}\n\\toprule\n & \\multicolumn{2}{c}{ADF} & \\multicolumn{2}{c}{Phillips-Perron}"
            " & \\multicolumn{2}{c}{KPSS} \\\\\n\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\\cmidrule(lr){6-7}\n"
            "Series & stat. & $p$ & stat. & $p$ & stat. & $p$ \\\\\n\\midrule\n")
    for r_ in rows:
        f.write(f"{lab[r_[0]]} & {r_[1]:.2f} & {r_[2]:.3f} & {r_[3]:.2f} & {r_[4]:.3f} & {r_[5]:.3f} & {r_[6]:.3f} \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")

# --------------------------------------------------------------------------- Table 3: OLS
# (1) replication of the 2022 specification: simple % changes, classical SEs
rep = sm.OLS(df["rWTI"], sm.add_constant(df[["rEPU", "rGPR"]]), missing="drop").fit()
# (2) revised: log changes, Newey-West (HAC) SEs, 6 lags
rev = sm.OLS(d["dWTI"], sm.add_constant(d[["dEPU", "dGPR"]])).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
# (3) revised + one lag of each regressor and of the dependent variable
X3 = pd.concat([d[["dEPU", "dGPR"]], d[["dWTI", "dEPU", "dGPR"]].shift(1).add_suffix("_l1")], axis=1)
rev3 = sm.OLS(d["dWTI"], sm.add_constant(X3), missing="drop").fit(cov_type="HAC", cov_kwds={"maxlags": 6})
R["ols_rep"] = {k: [float(rep.params[k]), float(rep.bse[k]), float(rep.pvalues[k])] for k in rep.params.index}
R["ols_rep_r2"] = float(rep.rsquared)
R["ols_rev"] = {k: [float(rev.params[k]), float(rev.bse[k]), float(rev.pvalues[k])] for k in rev.params.index}
R["ols_rev_r2"] = float(rev.rsquared)
R["ols_rev3"] = {k: [float(rev3.params[k]), float(rev3.bse[k]), float(rev3.pvalues[k])] for k in rev3.params.index}
R["ols_rev3_r2"] = float(rev3.rsquared)


def stars(p):
    return "^{***}" if p < 0.01 else "^{**}" if p < 0.05 else "^{*}" if p < 0.10 else ""


def cell(m, k):
    if k not in m.params.index:
        return "", ""
    return f"${m.params[k]:.4f}{stars(m.pvalues[k])}$", f"$({m.bse[k]:.4f})$"


names = [("const", "const", "const", "Constant"), ("rEPU", "dEPU", "dEPU", "EPU change"),
         ("rGPR", "dGPR", "dGPR", "GPR change"), (None, None, "dWTI_l1", "WTI change, $t-1$"),
         (None, None, "dEPU_l1", "EPU change, $t-1$"), (None, None, "dGPR_l1", "GPR change, $t-1$")]
with open(TAB / "tab3_ols.tex", "w") as f:
    f.write("\\begin{tabular}{lccc}\n\\toprule\n & (1) 2022 specification & (2) Revised & (3) Revised, lags \\\\\n"
            " & simple \\% changes, OLS SE & log changes, HAC SE & log changes, HAC SE \\\\\n\\midrule\n")
    for a, b, c, lbl in names:
        e1 = cell(rep, a) if a else ("", "")
        e2 = cell(rev, b) if b else ("", "")
        e3 = cell(rev3, c)
        f.write(f"{lbl} & {e1[0]} & {e2[0]} & {e3[0]} \\\\\n & {e1[1]} & {e2[1]} & {e3[1]} \\\\\n")
    f.write("\\midrule\n")
    f.write(f"$R^2$ & {rep.rsquared:.3f} & {rev.rsquared:.3f} & {rev3.rsquared:.3f} \\\\\n")
    f.write(f"Observations & {int(rep.nobs)} & {int(rev.nobs)} & {int(rev3.nobs)} \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")

# --------------------------------------------------------------------------- Table 4: Granger
def granger_p(y, x, lag):
    res = grangercausalitytests(pd.concat([y, x], axis=1).dropna(), maxlag=[lag])
    test = res[lag][0]["ssr_ftest"]
    return float(test[0]), float(test[1])


R["granger"] = {}
gr_rows = []
for xname, yname in [("dEPU", "dWTI"), ("dGPR", "dWTI"), ("dWTI", "dEPU"), ("dWTI", "dGPR")]:
    sel = VAR(d[[yname, xname]]).select_order(maxlags=12)
    lag_aic, lag_bic = max(1, int(sel.aic)), max(1, int(sel.bic))
    out = {}
    for tag, lag in [("aic", lag_aic), ("bic", lag_bic), ("orig3", 3)]:
        out[tag] = (lag,) + granger_p(d[yname], d[xname], lag)
    R["granger"][f"{xname}->{yname}"] = out
    gr_rows.append((xname, yname, out))
pretty = {"dWTI": "WTI", "dEPU": "EPU", "dGPR": "GPR"}
with open(TAB / "tab4_granger.tex", "w") as f:
    f.write("\\begin{tabular}{lcccc}\n\\toprule\n & \\multicolumn{2}{c}{Lag selected by AIC}"
            " & \\multicolumn{2}{c}{Lag selected by BIC} \\\\\n\\cmidrule(lr){2-3}\\cmidrule(lr){4-5}\n"
            "Null hypothesis & lag, $F$ & $p$ & lag, $F$ & $p$ \\\\\n\\midrule\n")
    for xname, yname, out in gr_rows:
        a, b = out["aic"], out["bic"]
        f.write(f"{pretty[xname]} $\\nrightarrow$ {pretty[yname]} & {a[0]}, {a[1]:.2f} & {a[2]:.3f} & "
                f"{b[0]}, {b[1]:.2f} & {b[2]:.3f} \\\\\n")
    f.write("\\bottomrule\n\\end{tabular}\n")
# replication of the 2022 tests on simple % changes
R["granger_2022_replication"] = {
    "EPU->WTI(3)": granger_p(df["rWTI"], df["rEPU"], 3),
    "GPR->WTI(3)": granger_p(df["rWTI"], df["rGPR"], 3),
    "WTI->GPR(1)": granger_p(df["rGPR"], df["rWTI"], 1),
}

# --------------------------------------------------------------------------- rolling correlation
roll = pd.DataFrame({"EPU": d["dWTI"].rolling(36).corr(d["dEPU"]),
                     "GPR": d["dWTI"].rolling(36).corr(d["dGPR"])})
fig, ax = plt.subplots(figsize=(6.3, 2.4))
ax.plot(roll.index, roll["EPU"], lw=1, color="k", label="WTI–EPU")
ax.plot(roll.index, roll["GPR"], lw=1, color="0.55", ls="--", label="WTI–GPR")
ax.axhline(0, color="0.3", lw=0.5)
ax.set_ylabel("36-month correlation")
ax.legend(frameon=False, ncol=2, loc="lower left")
fig.savefig(FIG / "fig4_rolling.pdf")
plt.close(fig)
R["roll"] = {k: {"min": float(roll[k].min()), "min_date": roll[k].idxmin().strftime("%B %Y"),
                 "max": float(roll[k].max()), "max_date": roll[k].idxmax().strftime("%B %Y"),
                 "mean": float(roll[k].mean())} for k in roll}
R["corr_full"] = {"EPU": float(d["dWTI"].corr(d["dEPU"])), "GPR": float(d["dWTI"].corr(d["dGPR"]))}

# --------------------------------------------------------------------------- wavelet coherence
dt, dj, s0 = 1.0, 1 / 12, 2.0
J = int(np.log2(64 / s0) / dj)   # periods from 2 to ~64 months
t = np.arange(len(d))
dates = d.index
bands = {"2-8": (2, 8), "8-16": (8, 16), "16-32": (16, 32), "32-64": (32, 64)}
windows = {"2001-2002": ("2001-01", "2002-12"), "2008-2009": ("2008-01", "2009-12"),
           "2014-2016": ("2014-06", "2016-06"), "2020-2022": ("2020-01", "2022-03")}
R["wtc"] = {}
for other, fname in [("dEPU", "fig2_wtc_epu.pdf"), ("dGPR", "fig3_wtc_gpr.pdf")]:
    x = d["dWTI"].values
    y = d[other].values
    WCT, aWCT, coi, freq, sig = pycwt.wct(x, y, dt, dj=dj, s0=s0, J=J, sig=True, significance_level=0.95,
                                          wavelet="morlet", normalize=True, cache=False)
    period = 1 / freq
    sig95 = np.ones([1, len(t)]) * sig[:, None]
    sig95 = WCT / sig95
    inside = period[:, None] <= coi[None, :]       # outside the cone of influence
    signif = (sig95 > 1) & inside

    # figure
    fig, ax = plt.subplots(figsize=(6.3, 3.2))
    cf = ax.contourf(t, np.log2(period), WCT, np.linspace(0, 1, 11), cmap="Greys", extend="neither")
    ax.contour(t, np.log2(period), sig95, [1], colors="k", linewidths=1.0)
    ax.fill_between(t, np.log2(coi), np.log2(period.max()), color="white", alpha=0.55, hatch="//",
                    edgecolor="0.6", lw=0)
    step_t, step_p = 6, 6
    for i in range(0, len(period), step_p):
        for j in range(0, len(t), step_t):
            if signif[i, j]:
                ph = aWCT[i, j]
                ax.quiver(t[j], np.log2(period[i]), np.cos(ph), np.sin(ph), scale=40, width=0.0025,
                          headwidth=4, headlength=4, color="k", pivot="middle")
    yt = [2, 4, 8, 16, 32, 64]
    ax.set_yticks(np.log2(yt))
    ax.set_yticklabels(yt)
    ax.set_ylim(np.log2(2), np.log2(64))
    ax.invert_yaxis()
    xt = [i for i, dd in enumerate(dates) if dd.month == 1 and dd.year % 2 == 0]
    ax.set_xticks(xt)
    ax.set_xticklabels([dates[i].year for i in xt])
    ax.set_ylabel("Period (months)")
    cb = fig.colorbar(cf, ax=ax, pad=0.02)
    cb.set_label("Coherence")
    fig.savefig(FIG / fname)
    plt.close(fig)

    # quantify significant regions
    res = {"share_sig_total": float(signif.sum() / inside.sum())}
    for bn, (lo, hi) in bands.items():
        m = (period >= lo) & (period < hi)
        res[f"band_{bn}"] = float(signif[m].sum() / max(1, inside[m].sum()))
    for wn, (a, b) in windows.items():
        mt = (dates >= a) & (dates <= b)
        res[f"win_{wn}"] = float(signif[:, mt].sum() / max(1, inside[:, mt].sum()))
    # phase in significant cells (phi = phase(WTI) - phase(other), calibrated on a known lag):
    # (0, pi/2) in phase, WTI leads; (-pi/2, 0) in phase, other leads;
    # (pi/2, pi) anti-phase, other leads; (-pi, -pi/2) anti-phase, WTI leads
    def wti_leads(a):
        return ((a > 0) & (a < np.pi / 2)) | (a < -np.pi / 2)

    ph = aWCT[signif]
    res["n_sig_cells"] = int(signif.sum())
    res["share_inphase"] = float(np.mean(np.abs(ph) < np.pi / 2)) if ph.size else None
    res["share_wti_leads"] = float(np.mean(wti_leads(ph))) if ph.size else None
    # significant regions listed by year and band (for the text)
    regions = []
    for bn, (lo, hi) in bands.items():
        m = (period >= lo) & (period < hi)
        yrs = sorted({dates[j].year for j in range(len(t)) if signif[m, j].any()})
        regions.append({"band": bn, "years": yrs})
    res["regions"] = regions
    # dominant phase per band
    for bn, (lo, hi) in bands.items():
        m = (period >= lo) & (period < hi)
        sub = aWCT[m][signif[m]]
        res[f"phase_{bn}"] = {"n": int(sub.size),
                              "inphase": float(np.mean(np.abs(sub) < np.pi / 2)) if sub.size else None,
                              "wti_leads": float(np.mean(wti_leads(sub))) if sub.size else None}
    # phase by episode and band (median phase in degrees, share in phase, share WTI leading)
    episodes = {"2000-2004": ("2000-01", "2004-12"), "2007-2010": ("2007-01", "2010-12"),
                "2014-2017": ("2014-01", "2017-12"), "2018-2022": ("2018-01", "2022-03")}
    res["episodes"] = {}
    for en, (a, b) in episodes.items():
        mt = np.asarray((dates >= a) & (dates <= b))
        for bn, (lo, hi) in bands.items():
            m = (period >= lo) & (period < hi)
            cells = signif & m[:, None] & mt[None, :]
            sub = aWCT[cells]
            if sub.size >= 10:
                res["episodes"][f"{en} | {bn}"] = {
                    "n": int(sub.size), "median_phase_deg": float(np.degrees(np.angle(np.mean(np.exp(1j * sub))))),
                    "inphase": float(np.mean(np.abs(sub) < np.pi / 2)), "wti_leads": float(np.mean(wti_leads(sub))),
                    "max_coh": float(WCT[cells].max())}
    R["wtc"][other] = res

json.dump(R, open(HERE / "results.json", "w"), indent=1, default=str)
print(json.dumps(R, indent=1, default=str)[:6000])
