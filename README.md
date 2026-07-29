# Alpha Commons

## Current Registry

The A-share daily MVP currently contains 13 auditable price-and-volume factors across momentum, reversal, volatility and liquidity. Browse the [factor catalog](docs/factors.md), inspect the machine-readable records in `registry/factors/`, or run `validate_registry()` to check that every entry has a source, availability policy, card and importable implementation.

面向多资产研究的**可发现、可运行、可验证、可复现**因子注册中心。首个可运行版本聚焦 A 股日频横截面因子；美股、期货、加密货币与高频市场通过同一份因子协议扩展。

> 这不是又一个公式清单。每个因子都必须有来源、数据契约、实现、可得性说明、测试和标准评估结果。

## 为什么存在

现有开源资源通常各有侧重：因子收录广、代码实现多、数据接口方便或评估工具成熟，但很少同时解决来源追溯、可得性、可重复实验和跨项目比较的问题。Alpha Commons 把这些环节放进同一个可审查的工作流。

## 首版能力

- 统一的 `FactorSpec`：声明市场、频率、字段、可得性滞后、换月规则和成本模型。
- 4 个 A 股日频基线因子：12-1 动量、5 日反转、20 日波动率、Amihud 非流动性。
- 长表 OHLCV 数据适配与强校验，避免隐式的数据口径错误。
- 横截面评估：覆盖率、Rank IC、分组收益和换手率。
- 可机器读取的因子注册表和人类可读的因子卡片。
- 可选 Qlib 适配器；其他市场在同一协议下预留扩展点。

## 快速开始

```bash
python -m venv .venv
.venv\\Scripts\\activate       # Windows PowerShell
pip install -e ".[dev]"
pytest
```

```python
import pandas as pd
from factor_registry import momentum_12_1, evaluate_cross_sectional

bars = pd.read_parquet("bars.parquet")
# bars: timestamp, instrument, open, high, low, close, volume
factor = momentum_12_1(bars)
report = evaluate_cross_sectional(factor, bars, horizons=(1, 5, 20))
print(report.summary)
```

输入数据采用长表格式，至少包含：`timestamp`、`instrument`、`close`。字段含义与额外市场字段见 [docs/data-contract.md](docs/data-contract.md)。

## 因子状态

| 状态 | 含义 |
| --- | --- |
| `experimental` | 有公式与测试，尚未完成统一基准评估 |
| `replicated` | 已依据公开来源完成可复现实现 |
| `validated` | 已通过指定数据集、时间范围和成本假设下的标准评估 |
| `deprecated` | 已发现问题或被更可靠版本替代 |

任何结果都不是投资建议，也不代表未来收益。

## 项目结构

```text
src/factor_registry/     核心协议、因子、适配器与评估器
registry/factors/        可机器读取的因子元数据
docs/factor-cards/       因子卡片：来源、直觉、数据与验证规则
tests/                   单元测试和防未来函数测试
```

## 路线图

1. A 股日频：经典价量与基本面因子、Qlib/Parquet 数据适配、标准报告。
2. 美股日频：点时点股票池、公司行为和财报可得性。
3. 期货日频：合约生命周期、连续合约和换月/期限结构规则。
4. 加密分钟/小时频：交易所、资金费率、基差与 24/7 日历。
5. 高频扩展：Tick/L2 数据契约、事件时间、成交概率与冲击成本。

## 致谢与上游项目

本项目借鉴并计划通过适配器连接下列开源项目；不复制其受限数据，也不移除原始作者署名或许可证。

- [QuantML](https://github.com/QuantMLResearch/QuantML)：因子图谱与资料组织。
- [quant-ohlcv-feature](https://github.com/YuxinSUN89/quant-ohlcv-feature)：模块化技术指标组织方式。
- [GetAstockFactors](https://github.com/hugo2046/GetAstockFactors)：A 股经典因子模型与数据口径参考。
- [FinHack](https://github.com/FinHackCN/finhack)：投研工作流与框架集成方向。
- [Alphalens Reloaded](https://github.com/stefan-jansen/alphalens-reloaded)：因子分析指标和报告范式。

详细的来源与许可政策见 [SOURCES.md](SOURCES.md)。
