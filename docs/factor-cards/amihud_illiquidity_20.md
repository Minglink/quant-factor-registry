# 20 日 Amihud 非流动性 (`amihud_illiquidity_20`)

计算过去 20 日的平均 `abs(日收益率) / 成交额`。若没有成交额，参考实现用 `close × volume` 近似。

低成交额标的的数值可能极端，实际研究通常需要流动性股票池、截尾或 winsorize 规则。该规则必须写进实验配置。

来源：Amihud (2002), *Illiquidity and stock returns*。
