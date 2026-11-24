# Financial market & oil volatility within distressed economies

**Wavelet coherence evidence from the early 21st century**

Final thesis — EDHEC Business School, International BBA (4th year, 2020/2021
programme). Thesis director: Ms Stepanyan. Final version: July 2022.

📄 **[Read the thesis (PDF)](thesis/Simons_EDHEC_thesis_oil-volatility-wavelet-coherence.pdf)** —
original version, unchanged.

📘 **[Revised edition, 2026 (PDF)](revised-edition-2026/Simons_EDHEC_thesis_revised-edition-2026.pdf)** —
same question and data, corrected text and re-run analysis (see below).

## Research question

What drives oil price fluctuations, how do crises affect them, and how strongly
do economic and geopolitical uncertainty interfere with the oil price — in
particular during distressed periods (2008 financial crisis, Covid-19, early
2022 tensions)?

## Data

Monthly series, January 2000 – March 2022 (267 observations):

| Variable | Description | Source |
|---|---|---|
| `WTI` | West Texas Intermediate crude oil price | FRED, Federal Reserve Bank of St. Louis |
| `EPU` | Economic Policy Uncertainty index (Baker, Bloom & Davis) | policyuncertainty.com |
| `GPR` | Geopolitical Risk index (Caldara & Iacoviello) | matteoiacoviello.com/gpr.htm |

`rWTI`, `rEPU`, `rGPR` are simple monthly percentage changes.

## Method

1. **Descriptive statistics and stationarity** — autocorrelation functions,
   Phillips-Perron unit-root tests, Jarque-Bera normality tests, on levels and
   on returns.
2. **Classical econometrics** — OLS regression of WTI returns on EPU and GPR
   returns, Granger causality tests, VAR lag selection.
3. **Wavelet coherence** (R package `biwavelet`, 100 Monte-Carlo
   randomisations) between WTI and EPU, and between WTI and GPR, to locate
   co-movement in both time and frequency.

## Main findings

- The regression approach was **not robust enough** to support a model or a
  conclusion on the WTI / EPU / GPR relationship.
- Wavelet coherence shows **significant co-movement** between oil returns and
  uncertainty, concentrated in crisis periods:
  - **EPU**: high coherence 2001–2005, a large cluster during the 2008
    financial crisis, a low-frequency spike in 2016 and the Covid period after
    2019;
  - **GPR**: weaker than expected — around 2001 (medium frequency), 2004 (low
    frequency) and after Covid;
  - a common **8-to-10-month band** appears for both indices.
- Economic policy uncertainty appears to matter more for oil than geopolitical
  risk over the sample.
- Limits: wavelet coherence does not give the direction of the effect. Further
  work suggested: directional analysis, macroeconomic controls (inflation), and
  a Brent benchmark.

## Revised edition (2026)

[`revised-edition-2026/`](revised-edition-2026/) re-runs the analysis on the
identical data in Python (`revised_analysis.py`, fully reproducible) with log
changes, a full unit-root battery, robust standard errors, two-way Granger tests
with lag selection, and wavelet coherence with Monte Carlo significance and phase
(lead–lag) analysis. It also corrects errors of the 2022 text (an erratum is
included). Main revised findings:

- WTI is non-stationary in levels; all models use monthly log changes.
- Economic policy uncertainty is negatively associated with oil price changes
  (elasticity −0.074, HAC p = 0.026), with a further lagged effect; geopolitical
  risk has no significant average effect.
- Granger evidence is weak: EPU → WTI only with one lag (p = 0.035); the 2022
  tests described as significant were not.
- WTI–EPU coherence is concentrated in 2001–2004, 2007–2010 and 2018–2021 at
  8–16-month horizons, mostly in anti-phase; uncertainty leads oil in the first
  two episodes, oil leads during the pandemic. WTI–GPR coherence is confined to
  2000–2004.

## Repository

```
thesis/                final thesis (PDF, original)
code/                  final R script used for the thesis
data/                  input data (levels workbook, wavelet pairs, CSV with returns)
revised-edition-2026/  revised edition (PDF), Python analysis, LaTeX source, figures, tables
paper-2026/            2026 follow-up paper (draft)
```

To run the script, see the reproduction notes at the top of
[`code/thesis_code.R`](code/thesis_code.R).

## 2026 follow-up

[`paper-2026/paper-1-oil-wavelet.pdf`](paper-2026/paper-1-oil-wavelet.pdf) —
*Geopolitical Risk, Economic Policy Uncertainty, and Oil Price Volatility: A
Multi-Resolution Wavelet and DCC-GARCH Approach, 2000–2024* (draft, May 2026).
It revisits the thesis with a longer sample, return-based specifications,
DCC-GARCH and a quantile causality test.

## Data credits

- Baker, S. R., Bloom, N. & Davis, S. J. (2016). *Measuring Economic Policy
  Uncertainty.* Quarterly Journal of Economics.
- Caldara, D. & Iacoviello, M. (2022). *Measuring Geopolitical Risk.* American
  Economic Review.
- WTI spot price: U.S. Energy Information Administration, via FRED.
