# A-Share Daily Factor Catalog

All entries use canonical long-form daily data and are evaluated only after the close. `replicated` means the formula has a cited source and a tested implementation; it does not assert investment efficacy. `experimental` entries require broader benchmark evidence.

| Category | Factor | Required market fields | Status |
| --- | --- | --- | --- |
| Momentum | `momentum_12_1`, `momentum_20`, `momentum_60` | close | replicated |
| Reversal | `reversal_5`, `reversal_20` | close | replicated |
| Volatility | `volatility_20`, `downside_volatility_20`, `high_low_range_20` | close; high/low where stated | replicated |
| Volatility | `return_skewness_20` | close | experimental |
| Liquidity | `amihud_illiquidity_20`, `average_dollar_volume_20` | close, volume; turnover optional | replicated |
| Liquidity | `volume_volatility_20`, `volume_price_correlation_20` | volume; close where stated | experimental |

Each name links to a machine-readable record in `registry/factors/` and an independent factor card in `docs/factor-cards/`.
