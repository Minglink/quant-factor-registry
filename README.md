# Alpha Commons

[![Test](https://github.com/Minglink/quant-factor-registry/actions/workflows/test.yml/badge.svg)](https://github.com/Minglink/quant-factor-registry/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**面向 A 股研究者的可发现、可运行、可验证、可复现因子注册中心。**

Alpha Commons 不是“再收集一批公式”的仓库。这里的基本单位不是函数，而是一份可以被其他研究者独立复查的**因子档案**：它必须说明公式、来源、数据口径、何时可得、如何计算、在什么假设下评估，以及当前证据支持它到什么程度。

首个版本只解决一件事：把 **A 股日频横截面因子** 从文献或研报，带到可重复的标准实验。美股、期货、加密货币与高频市场会沿用同一协议扩展，但不会在 A 股 MVP 尚未打磨完成前混入一套粗糙的通用公式。

## What Makes It Different

| 常见做法 | Alpha Commons 的要求 |
| --- | --- |
| 收录一个公式或一段代码 | 收录一份因子档案：代码、来源、字段、可得性、状态和版本缺一不可 |
| 只展示最佳回测区间 | 统一报告全样本、市场状态、换手和成本后的结果 |
| 把“可计算”当成“有效” | 明确区分 `experimental`、`replicated`、`validated` 与 `deprecated` |
| 把数据细节留在 Notebook 里 | 数据契约和股票池规则是可审查的实验输入 |
| 因子越多越好 | 优先收录能被可信复现、比较和组合的因子 |

一个条目要进入注册表，至少通过以下检查：

```text
公开来源 / 许可证
        +
机器可读元数据 ----> 标准 Python 实现 ----> 单元测试
        +                         +
数据字段与可得性规则              标准化评估：IC、分组、换手、成本、稳定性
        +                         +
                    人类可读因子卡片与可复现实验配置
```

## Current Release

当前 MVP 已收录 **13 个 A 股日频价量因子**，覆盖动量、反转、波动率和流动性四类：

- `replicated`：10 个已有公开来源、独立实现和测试的因子。
- `experimental`：3 个已实现但尚未积累统一基准证据的候选因子。
- 每个条目都有 YAML 注册记录、独立因子卡片和可解析的 Python 实现引用。

浏览完整目录：[因子超市 / Factor Catalog](docs/factors.md)。

这不是对任何因子未来收益能力的背书。`replicated` 仅表示公式和实现可复查；只有给出明确数据版本、股票池、时间范围和成本假设的证据后，条目才应升级为 `validated`。

## A Factor Is a Record, Not Just a Function

每个因子都有同一份机器可读档案。以 `momentum_12_1` 为例：

```yaml
factor_id: momentum_12_1
name_zh: 12-1 月动量
category: momentum
asset_classes: [cn_equity]
frequency: 1d
required_fields: [timestamp, instrument, close]
availability_policy: close is known after the session; trade next session
source_urls: [https://doi.org/10.1111/j.1540-6261.1993.tb04702.x]
implementation: factor_registry.factors.equity:momentum_12_1
status: replicated
version: 0.1.0
```

对应的因子卡片还会解释经济直觉、复权和停牌规则、稳健性检验、相关因子和已知局限。查看：[12-1 月动量卡片](docs/factor-cards/momentum_12_1.md)。

## Start Here

```bash
git clone https://github.com/Minglink/quant-factor-registry.git
cd quant-factor-registry
python -m venv .venv
.venv\Scripts\activate       # Windows PowerShell
pip install -e ".[dev]"
pytest -q
```

数据使用长表格式，一行表示某个标的在某个可知时点的一次观测：

```python
import pandas as pd

from factor_registry import evaluate_cross_sectional, momentum_12_1

bars = pd.read_parquet("bars.parquet")
# required: timestamp, instrument, close
# optional: open, high, low, volume, turnover

factor = momentum_12_1(bars)
report = evaluate_cross_sectional(
    factor,
    bars,
    horizons=(1, 5, 20),
    quantiles=5,
    one_way_cost_bps=10,
)

print(report.summary)
print(report.daily)
```

```python
from factor_registry import validate_registry

validate_registry()  # cards, sources, fields and implementation references must all resolve
```

字段含义、时间戳和各市场扩展字段见 [数据契约](docs/data-contract.md)。仓库不分发市场数据。

## What the Evaluator Reports

借鉴 Alphalens 的“先清洗、再诊断”思路，当前横截面评估器提供：

| 维度 | 当前输出 |
| --- | --- |
| 预测能力 | Rank IC、ICIR、覆盖率 |
| 组合结果 | 分组多空毛价差、成本后价差、累计净值 |
| 可交易性 | 顶部与底部组合的单边换手、显式单边成本假设 |
| 稳健性 | 可按外部传入的市场状态标签拆分表现 |
| 风险控制接口 | 可传入点时点行业、市值或风险模型预处理函数 |

报告不是回测器的替代品。它负责回答“因子是否有稳定预测信息”；真实策略仍需在明确的交易日历、涨跌停、停牌、T+1、容量和撮合假设下验证。

## Current Factor Catalog

| 类别 | 因子 | 状态 |
| --- | --- | --- |
| 动量 | `momentum_12_1`, `momentum_20`, `momentum_60` | replicated |
| 反转 | `reversal_5`, `reversal_20` | replicated |
| 波动率 | `volatility_20`, `downside_volatility_20`, `high_low_range_20` | replicated |
| 波动率 | `return_skewness_20` | experimental |
| 流动性 | `amihud_illiquidity_20`, `average_dollar_volume_20` | replicated |
| 流动性 | `volume_volatility_20`, `volume_price_correlation_20` | experimental |

完整字段、来源、卡片和实现链接都在 [`registry/factors/`](registry/factors/) 与 [因子目录](docs/factors.md) 中。

## Research Rules

Alpha Commons 把以下规则视为研究结论的一部分，而不是可选备注：

1. **不允许未来数据。** `timestamp` 表示策略真正可使用数据的时点；财务数据必须使用公告可得日期，而不是报告期末。
2. **不允许幸存者偏差。** A 股实验须记录股票池、新股、ST、停牌、退市和涨跌停处理；美股扩展还须使用点时点成分和退市数据。
3. **不允许隐藏成本。** 所有标准结果都必须披露调仓频率、换手、成本和不可交易规则。
4. **不复制来源不明或许可不兼容的代码与数据。** 外部成果采用引用、适配或独立重实现，并保留出处与许可证。

更多约束见 [贡献指南](CONTRIBUTING.md) 与 [来源和许可证政策](SOURCES.md)。

## Why These Projects Matter

Alpha Commons 从已有开源项目吸收不同部分，但不把它们混成一个臃肿框架：

| 项目 | 借鉴重点 | Alpha Commons 的处理方式 |
| --- | --- | --- |
| [QuantML](https://github.com/QuantMLResearch/QuantML) | 大规模因子分类、论文与资料索引 | 用于构建可检索因子图谱，不以收录数量作为验证结论 |
| [quant-ohlcv-feature](https://github.com/YuxinSUN89/quant-ohlcv-feature) | 单因子函数和模块化指标组织 | 采用统一输入输出契约，每个实现保持小而可测试 |
| [GetAstockFactors](https://github.com/hugo2046/GetAstockFactors) | A 股股票池、复权和不可交易规则的重要性 | 将这些市场口径写入数据契约和实验配置，而不是隐含在数据里 |
| [FinHack](https://github.com/FinHackCN/finhack) | 数据、因子、挖掘、回测的完整工作流 | 预留研究和策略接口，但核心仓库只负责可复现的因子层 |
| [Alphalens Reloaded](https://github.com/stefan-jansen/alphalens-reloaded) | IC、分组收益、换手与诊断报告范式 | 提供轻量、显式成本和稳定性假设的标准评估层 |

我们不复制上述项目的受限数据或许可证不兼容代码。具体归属政策见 [SOURCES.md](SOURCES.md)。

## Repository Map

```text
src/factor_registry/
  core.py                 # FactorSpec / FactorOutput: shared factor protocol
  factors/                # small, testable reference implementations
  adapters/               # canonical data and Qlib adapters
  evaluation/             # cross-sectional diagnostics
  registry_validation.py  # registry, card, source and implementation checks

registry/factors/         # machine-readable factor records
docs/factor-cards/        # human-readable factor dossiers
docs/                     # architecture, data contract and catalog
tests/                    # implementation and registry contract tests
```

## Roadmap: One Protocol, Market-Specific Rules

发布节奏是 A 股日频优先；后续不是简单地把公式复制到不同资产，而是为每个市场增加必要的数据契约与评估器。

| 阶段 | 重点 | 必须新增的规则 |
| --- | --- | --- |
| A 股日频 | 基本面、估值、质量、成长与规模因子 | 点时点财务可得性、股票池和可交易性 |
| 美股日频 | 价值、质量、预期修正、事件因子 | 退市、拆分分红、盘前盘后、点时点指数成分 |
| 期货日频 | 趋势、期限结构、持仓量、跨期价差 | 到期、连续合约、换月、夜盘、保证金和涨跌停 |
| 加密小时/分钟 | 资金费率、基差、跨交易所和链上因子 | 24/7 日历、交易所、币种下架、费用与资金费率 |
| 高频扩展 | 订单流、微价格、盘口失衡 | Tick/L2、事件时间、延迟、排队、冲击成本和成交概率 |

最终目标不是“支持很多市场的公式库”，而是能够清楚回答：**这个因子在哪个市场、什么频率、依赖什么数据、在何种可得性和成本假设下成立？**

## Contributing

欢迎提交新因子、数据适配器、基准实验或改进卡片。每个贡献至少需要：

1. 标准实现与单元测试；
2. YAML 注册记录和因子卡片；
3. 来源、许可证、字段与可得性说明；
4. 可复现实验配置或明确标记为 `experimental`；
5. 不引入未授权市场数据。

提交前运行：

```bash
pytest -q
```

## License

项目原创代码采用 [MIT License](LICENSE)。因子来源、论文和外部项目的归属不因本仓库而改变。所有研究输出仅供研究与教育使用，不构成投资建议。
