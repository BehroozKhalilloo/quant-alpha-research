# Liquidity-Adjusted Reversal Research Report

This report is generated from local research artifacts. It intentionally does not hard-code performance claims.

## Generated Figures

![Cumulative returns](figures/cumulative_returns.png)

![Drawdown](figures/drawdown.png)

![Rolling Sharpe](figures/rolling_sharpe.png)

![Turnover](figures/turnover.png)

![IC time series](figures/ic_time_series.png)

![IC by year](figures/ic_by_year.png)

![Decile forward returns](figures/decile_forward_returns.png)

![Beta exposure](figures/beta_exposure.png)

![Candidate Sharpe Comparison](figures/candidate_sharpe.png)

![Transaction Cost Sensitivity](figures/cost_sensitivity.png)

![Rolling 126-Day Sharpe](figures/rolling_126d_sharpe.png)

## IC Summary

| metric | mean | std | t_stat | count |
| --- | --- | --- | --- | --- |
| pearson | 0.0168663 | 0.261266 | 2.92788 | 2057 |
| spearman | 0.0193712 | 0.254064 | 3.45805 | 2057 |

## Newey-West IC Inference

| metric | mean | nw_t_stat | count |
| --- | --- | --- | --- |
| pearson | 0.0168663 | 1.81043 | 2057 |
| spearman | 0.0193712 | 2.14281 | 2057 |

## Backtest Summary

| metric | 0 |
| --- | --- |
| annualized_return | 0.195163 |
| annualized_volatility | 0.127046 |
| sharpe_ratio | 1.53615 |
| sortino_ratio | 2.19513 |
| max_drawdown | -0.102241 |
| hit_rate | 0.549632 |

## Naive Reversal Baseline

| metric | 0 |
| --- | --- |
| annualized_return | -0.119762 |
| annualized_volatility | 0.13039 |
| sharpe_ratio | -0.918495 |
| sortino_ratio | -1.32447 |
| max_drawdown | -0.702693 |
| hit_rate | 0.470061 |

## Robustness Checks

| metric | base_feature | direction | vol_adjust | liquidity_threshold | horizon | holding_period | sleeves | train_rank_ic | train_rank_ic_t | test_rank_ic | test_rank_ic_t | test_ic_count | ann_return | ann_vol | sharpe | sortino | max_drawdown | hit_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| multi_sleeve_blend | blend | blend | False | 0 | 5 | 5 | {'reversal_5d': 0.8, 'residual_reversal_1d': 0.1, 'momentum_21d': 0.05, 'quality_proxy': 0.05} | 0.0304438 | 3.72617 | 0.00992462 | 1.29148 | 1110 | 0.195163 | 0.127046 | 1.53615 | 2.19513 | -0.102241 | 0.549632 |
| default_5d_reversal | return_5d | reversal | False | 0 | 5 | 5 |  | 0.0272775 | 3.3846 | 0.0127833 | 1.64164 | 1110 | 0.0599446 | 0.133461 | 0.449155 | 0.618106 | -0.20598 | 0.522463 |
| one_day_reversal | return_1d | reversal | False | 0 | 1 | 1 |  | 0.00489377 | 0.607159 | 0.00349436 | 0.432243 | 1114 | -0.121166 | 0.130787 | -0.926438 | -1.33682 | -0.702693 | 0.469805 |
| residual_1d_vol_adjusted | residual_1d_return | reversal | True | 0.4 | 1 | 1 |  | 0.00239028 | 0.26645 | -0.00555367 | -0.653609 | 1106 | -0.0130804 | 0.123484 | -0.105928 | -0.151129 | -0.224977 | 0.489231 |
| twenty_one_day_momentum | momentum_21d | momentum | False | 0 | 5 | 5 |  | -0.0147972 | -1.93167 | -0.0100634 | -1.28715 | 1110 | -0.00342768 | 0.132033 | -0.0259608 | -0.0362356 | -0.313932 | 0.502765 |

## Sleeve Ablation

| metric | base_feature | direction | vol_adjust | liquidity_threshold | horizon | holding_period | sleeves | train_rank_ic | train_rank_ic_t | test_rank_ic | test_rank_ic_t | test_ic_count | ann_return | ann_vol | sharpe | sortino | max_drawdown | hit_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| full_blend | blend | blend | False | 0 | 5 | 5 | {'reversal_5d': 0.8, 'residual_reversal_1d': 0.1, 'momentum_21d': 0.05, 'quality_proxy': 0.05} | 0.0304438 | 3.72617 | 0.00992462 | 1.29148 | 1110 | 0.195163 | 0.127046 | 1.53615 | 2.19513 | -0.102241 | 0.549632 |
| minus_reversal_5d | blend | blend | False | 0 | 5 | 5 | {'residual_reversal_1d': 0.5, 'momentum_21d': 0.25, 'quality_proxy': 0.25} | -0.0108141 | -1.40881 | -0.00771916 | -1.08262 | 1110 | -0.176184 | 0.0845303 | -2.08427 | -3.86421 | -0.0288677 | 0.5 |
| minus_residual_reversal_1d | blend | blend | False | 0 | 5 | 5 | {'reversal_5d': 0.888888888888889, 'momentum_21d': 0.05555555555555556, 'quality_proxy': 0.05555555555555556} | 0.0279844 | 3.48465 | 0.0113813 | 1.466 | 1110 | 0.0672396 | 0.1324 | 0.50785 | 0.695428 | -0.186862 | 0.52381 |
| minus_momentum_21d | blend | blend | False | 0 | 5 | 5 | {'reversal_5d': 0.8421052631578947, 'residual_reversal_1d': 0.10526315789473684, 'quality_proxy': 0.05263157894736842} | 0.0296384 | 3.61921 | 0.0101823 | 1.3214 | 1110 | 0.132321 | 0.130101 | 1.01706 | 1.45562 | -0.109224 | 0.527491 |
| minus_quality_proxy | blend | blend | False | 0 | 5 | 5 | {'reversal_5d': 0.8421052631578947, 'residual_reversal_1d': 0.10526315789473684, 'momentum_21d': 0.05263157894736842} | 0.0304904 | 3.71387 | 0.0115154 | 1.49901 | 1110 | 0.1274 | 0.122159 | 1.0429 | 1.42867 | -0.143361 | 0.535714 |

## Walk-Forward Yearly IC

| metric | rank_ic | nw_t_stat | count |
| --- | --- | --- | --- |
| 2018 | 0.0888888 | 3.71988 | 190 |
| 2019 | 0.0189894 | 1.02625 | 252 |
| 2020 | 0.0245071 | 0.750929 | 253 |
| 2021 | 0.00379252 | 0.16212 | 252 |
| 2022 | 0.0423148 | 1.66849 | 251 |
| 2023 | -0.0358845 | -1.1423 | 250 |
| 2024 | 0.0144161 | 0.61049 | 252 |
| 2025 | 0.0136771 | 0.57032 | 250 |
| 2026 | 0.0216288 | 0.550159 | 107 |

## Parameter Sensitivity

| metric | base_feature | direction | liquidity_threshold | vol_adjust | rank_ic | nw_t_stat | count |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | return_1d | reversal | 0 | False | 0.00885531 | 1.60665 | 2098 |
| 1 | return_1d | reversal | 0 | True | 0.00845668 | 1.54161 | 2096 |
| 2 | return_1d | reversal | 0.4 | False | 0.0104789 | 1.61289 | 2086 |
| 3 | return_1d | reversal | 0.4 | True | 0.0111037 | 1.74847 | 2084 |
| 4 | return_1d | reversal | 0.6 | False | 0.0138808 | 1.76032 | 2068 |
| 5 | return_1d | reversal | 0.6 | True | 0.0144144 | 1.89571 | 2066 |
| 6 | return_5d | reversal | 0 | False | 0.019609 | 2.1494 | 2098 |
| 7 | return_5d | reversal | 0 | True | 0.0181878 | 1.99268 | 2096 |
| 8 | return_5d | reversal | 0.4 | False | 0.0197166 | 1.9593 | 2086 |
| 9 | return_5d | reversal | 0.4 | True | 0.0192265 | 1.92772 | 2084 |
| 10 | return_5d | reversal | 0.6 | False | 0.0227871 | 2.02818 | 2068 |
| 11 | return_5d | reversal | 0.6 | True | 0.0216642 | 1.96273 | 2066 |
| 12 | momentum_21d | momentum | 0 | False | -0.0122903 | -1.28963 | 2096 |
| 13 | momentum_21d | momentum | 0 | True | -0.0104197 | -1.09692 | 2096 |
| 14 | momentum_21d | momentum | 0.4 | False | -0.0101631 | -0.942895 | 2084 |
| 15 | momentum_21d | momentum | 0.4 | True | -0.00775325 | -0.733657 | 2084 |
| 16 | momentum_21d | momentum | 0.6 | False | -0.0187458 | -1.56494 | 2066 |
| 17 | momentum_21d | momentum | 0.6 | True | -0.02138 | -1.81039 | 2066 |
| 18 | residual_1d_return | reversal | 0 | False | 0.0052107 | 0.942797 | 2057 |
| 19 | residual_1d_return | reversal | 0 | True | 0.00498025 | 0.914702 | 2057 |

## False Discovery Report

| metric | p_value | bh_reject | bh_q_value |
| --- | --- | --- | --- |
| multi_sleeve_blend | 0.196536 | False | 0.33007 |
| default_5d_reversal | 0.100665 | False | 0.33007 |
| one_day_reversal | 0.665565 | False | 0.665565 |
| residual_1d_vol_adjusted | 0.513364 | False | 0.641705 |
| twenty_one_day_momentum | 0.198042 | False | 0.33007 |

## Transaction Cost Sensitivity

| metric | annualized_return | annualized_volatility | sharpe_ratio | sortino_ratio | max_drawdown | hit_rate |
| --- | --- | --- | --- | --- | --- | --- |
| 0.0 | 0.244757 | 0.126931 | 1.92826 | 2.74813 | -0.0985967 | 0.551471 |
| 2.0 | 0.224919 | 0.126972 | 1.7714 | 2.52727 | -0.100056 | 0.551471 |
| 5.0 | 0.195163 | 0.127046 | 1.53615 | 2.19513 | -0.102241 | 0.549632 |
| 10.0 | 0.145569 | 0.127204 | 1.14438 | 1.64003 | -0.105871 | 0.538603 |
| 20.0 | 0.046381 | 0.127643 | 0.363365 | 0.523892 | -0.168846 | 0.509191 |

## Capacity Analysis

| metric | avg_impact_bps | p95_participation | max_participation | annualized_return_after_impact | annualized_vol_after_impact | sharpe_after_impact |
| --- | --- | --- | --- | --- | --- | --- |
| 1000000 | 5.329 | 8.32572e-05 | 0.000869941 | 0.110466 | 0.127636 | 0.865477 |
| 10000000 | 16.8518 | 0.000832572 | 0.00869941 | -0.179908 | 0.131046 | -1.37286 |
| 50000000 | 37.6817 | 0.00416286 | 0.0434971 | -0.704823 | 0.143122 | -4.92465 |
| 100000000 | 53.29 | 0.00832572 | 0.0869941 | -1.09815 | 0.156246 | -7.02836 |

## Bootstrap Confidence Intervals

| metric | p05 | median | p95 |
| --- | --- | --- | --- |
| annualized_return | 0.0272207 | 0.164729 | 0.296186 |
| sharpe_ratio | 0.209649 | 1.30121 | 2.39354 |
| max_drawdown | -0.187837 | -0.108899 | -0.0673464 |

## Data Quality Summary

| metric | rows_flagged | columns |
| --- | --- | --- |
| missing_by_ticker | 50 | low,open,volume,high,close,adj_close |
| nonpositive_prices | 0 | open,high,low,close,adj_close |
| negative_volume | 0 | volume |
| stale_prices | 0 | is_stale |
| extreme_returns | 2 | return |
| zero_volume | 0 | zero_volume |
| daily_coverage | 2123 | coverage |

## Regime Summary

| metric | count | annualized_return | annualized_volatility | sharpe_ratio | sortino_ratio | max_drawdown | hit_rate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ('market_regime', 'negative_21d_trend') | 191 | -0.23537 | 0.128597 | -1.83029 | -2.14434 | -0.22779 | 0.47644 |
| ('market_regime', 'positive_21d_trend') | 353 | 0.428114 | 0.123926 | 3.4546 | 6.12471 | -0.0397335 | 0.589235 |
| ('vol_regime', 'high_vol') | 282 | 0.184218 | 0.152379 | 1.20895 | 1.73638 | -0.135226 | 0.535461 |
| ('vol_regime', 'low_vol') | 262 | 0.206944 | 0.0926321 | 2.23404 | 3.522 | -0.06324 | 0.564885 |

## Largest Drawdowns

| metric | start | trough | recovery | max_drawdown | days_to_trough | days_to_recovery |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | 2025-02-12 | 2025-05-14 | 2026-04-23 | -0.102241 | 91 | 435 |
| 1 | 2020-06-19 | 2021-11-04 | 2022-05-13 | -0.0884392 | 503 | 693 |
| 2 | 2023-01-12 | 2023-05-22 | 2024-12-11 | -0.0791374 | 130 | 699 |
| 3 | 2018-07-02 | 2018-10-19 | 2018-11-26 | -0.0412804 | 109 | 147 |
| 4 | 2020-03-11 | 2020-03-23 | 2020-03-24 | -0.0282847 | 12 | 13 |

## Interpretation

The selected multi-sleeve blend has positive full-sample IC, positive pre/post split rank IC, stronger Sharpe and drawdown than the pure reversal sleeve, and remains positive across the displayed transaction-cost stress range. Bootstrap intervals and rolling diagnostics make the result easier to audit. Regime analysis shows the strategy is materially stronger in positive 21-day market trends and weaker in negative trend regimes, so the evidence is stronger than the single-sleeve baseline but still not production proof.

## Disclaimer

This repository is for research and education only. It is not investment advice and does not include live trading or broker execution.
