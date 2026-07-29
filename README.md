# Alpha Commons

[![Test](https://github.com/Minglink/quant-factor-registry/actions/workflows/test.yml/badge.svg)](https://github.com/Minglink/quant-factor-registry/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Alpha Commons 是一个面向 A 股日频研究的因子注册库。它记录因子的定义、来源、数据要求、实现和评估口径，方便研究者查找、运行和复查。

仓库当前不保存行情或财务数据，也不提供“万能回测”。重点是把一个因子从文献、研报或已有想法，整理成可以在同一套约定下比较的研究对象。

## 现在有什么

当前收录 13 个价量因子，覆盖动量、反转、波动率和流动性。完整列表见 [因子目录](docs/factors.md)。

| 状态 | 数量 | 含义 |
| --- | ---: | --- |
| `replicated` | 10 | 有公开来源、独立实现和测试 |
| `experimental` | 3 | 可以运行，但还没有足够的统一基准证据 |

每个注册条目包含：

- YAML 元数据：分类、市场、频率、字段、来源、版本和状态；
- Markdown 因子卡片：公式、经济直觉、可得性、限制和验证建议；
- Python 实现和单元测试；
- 可被 `validate_registry()` 自动检查的实现、卡片和来源链接。

`replicated` 表示公式和实现可以复查，不等于“因子有效”或“可以直接交易”。升级为 `validated` 时，需要给出数据版本、股票池、区间、成本和实验结果。

## 快速开始

```bash
git clone https://github.com/Minglink/quant-factor-registry.git
cd quant-factor-registry
python -m venv .venv
.venv\Scripts\activate       # Windows PowerShell
pip install -e ".[dev]"
pytest -q
```

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
```

```python
from factor_registry import validate_registry

validate_registry()
```

## 因子是怎样收录的

以 `momentum_12_1` 为例，注册表会声明如下内容：

```yaml
factor_id: momentum_12_1
name_zh: 12-1 月动量
category: momentum
asset_classes: [cn_equity]
frequency: 1d
required_fields: [timestamp, instrument, close]
availability_policy: close is known after the session; trade next session
implementation: factor_registry.factors.equity:momentum_12_1
status: replicated
```

对应的 [因子卡片](docs/factor-cards/momentum_12_1.md) 会补充来源、复权口径、停牌和涨跌停处理、相关因子及验证建议。

新因子进入仓库前应满足：

1. 有来源和许可证说明；
2. 明确需要的字段，以及数据何时可被策略使用；
3. 使用统一输入输出格式，并有测试；
4. 有 YAML 条目和因子卡片；
5. 没有实验结果时，状态标为 `experimental`。

## 评估口径

横截面评估器目前提供 Rank IC、ICIR、覆盖率、分组多空价差、换手、显式成本后的价差和累计净值。也可以传入市场状态标签，查看不同阶段的表现；行业、市值或风险模型中性化由调用方以点时点数据预处理后传入。

报告用于检查预测信息，不替代策略回测。A 股实验仍应明确股票池、新股、ST、停牌、退市、涨跌停、T+1、调仓频率和容量假设。

## 数据约定

输入采用长表格式：一行是一个标的在一个可知时间点的观测。最少需要 `timestamp`、`instrument`、`close`。字段说明和市场扩展字段见 [数据契约](docs/data-contract.md)。

财务数据必须按公告可得时间处理，不能直接按报告期末回填；股票池不能只保留今天仍存在的股票。仓库不分发数据，也不接受未授权数据提交。

## 目录

```text
src/factor_registry/     核心协议、因子、适配器和评估器
registry/factors/        机器可读的因子元数据
docs/factor-cards/       因子卡片
docs/                    数据契约、架构和因子目录
tests/                   实现与注册表测试
```

## 参考项目

- [QuantML](https://github.com/QuantMLResearch/QuantML)：因子分类和资料索引。
- [quant-ohlcv-feature](https://github.com/YuxinSUN89/quant-ohlcv-feature)：模块化的单因子实现方式。
- [GetAstockFactors](https://github.com/hugo2046/GetAstockFactors)：A 股股票池、复权和不可交易规则的参考。
- [FinHack](https://github.com/FinHackCN/finhack)：数据、因子、回测之间的工作流。
- [Alphalens Reloaded](https://github.com/stefan-jansen/alphalens-reloaded)：IC、分组收益和换手分析的报告方式。

本项目不复制这些项目的受限数据或许可证不兼容代码。来源和许可说明见 [SOURCES.md](SOURCES.md)。

## 后续

先完成 A 股日频的基本面、估值、质量、成长和规模因子，并补齐点时点财务数据适配。之后再按各自的数据与交易规则扩展：美股需要退市和公司行为，期货需要合约生命周期和换月，加密需要交易所与资金费率，高频需要 Tick/L2、延迟和冲击成本。

## 贡献

欢迎提交因子、数据适配器、基准实验或文档改进。提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，并运行：

```bash
pytest -q
```

项目原创代码采用 [MIT License](LICENSE)。所有研究输出仅供研究与教育使用，不构成投资建议。
