# 数据契约

Alpha Commons 使用长表数据；一行代表一个标的在一个可知时间点的观测。

| 字段 | 所有市场 | 说明 |
| --- | --- | --- |
| `timestamp` | 是 | UTC 时间戳；表达数据对策略可用的时间 |
| `instrument` | 是 | 稳定的标的 ID，不能仅依赖显示代码 |
| `close` | 日频/分钟频常用 | 复权、结算或标记价格必须在因子卡中声明 |
| `open/high/low/volume/turnover` | 可选 | 行情与成交字段 |
| `venue/currency` | 多市场推荐 | 交易场所与计价货币 |

## 市场扩展字段

| 市场 | 字段 | 必须在因子卡中声明的规则 |
| --- | --- | --- |
| 美股 | `split_factor`, `dividend`, `filing_timestamp` | 点时点股票池、退市与公司行为 |
| 期货 | `expiry_date`, `open_interest`, `settlement_price` | 主力/连续合约、展期与夜盘 |
| 加密 | `funding_rate`, `mark_price`, `exchange` | 交易所、资金费、24/7 与下架币种 |
| 高频 | `bid`, `ask`, `bid_size`, `ask_size`, `trade_side` | 事件时间、撮合、延迟与盘口重建 |

数据适配器必须在导入时完成：时间统一、去重、字段映射以及源数据可得性处理。项目不分发行情和逐笔数据。
