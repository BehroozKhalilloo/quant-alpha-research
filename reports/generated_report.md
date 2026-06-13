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

## IC Summary

| metric | mean | std | t_stat | count |
| --- | --- | --- | --- | --- |
| pearson | 0.0168663 | 0.261266 | 2.92788 | 2057 |
| spearman | 0.0193712 | 0.254064 | 3.45805 | 2057 |

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

## Transaction Cost Sensitivity

| metric | annualized_return | annualized_volatility | sharpe_ratio | sortino_ratio | max_drawdown | hit_rate |
| --- | --- | --- | --- | --- | --- | --- |
| 0.0 | 0.244757 | 0.126931 | 1.92826 | 2.74813 | -0.0985967 | 0.551471 |
| 2.0 | 0.224919 | 0.126972 | 1.7714 | 2.52727 | -0.100056 | 0.551471 |
| 5.0 | 0.195163 | 0.127046 | 1.53615 | 2.19513 | -0.102241 | 0.549632 |
| 10.0 | 0.145569 | 0.127204 | 1.14438 | 1.64003 | -0.105871 | 0.538603 |
| 20.0 | 0.046381 | 0.127643 | 0.363365 | 0.523892 | -0.168846 | 0.509191 |

## Interpretation

The selected multi-sleeve blend has positive full-sample IC, positive pre/post split rank IC, stronger Sharpe and drawdown than the pure reversal sleeve, and remains positive across the displayed transaction-cost stress range. The evidence is stronger than the single-sleeve baseline, but it is still research evidence: the default universe is not point-in-time, the quality sleeve is a price/volume proxy rather than a fundamental factor, and live implementation details are intentionally out of scope.

## Disclaimer

This repository is for research and education only. It is not investment advice and does not include live trading or broker execution.
