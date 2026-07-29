# 贡献指南

欢迎提交因子、数据适配器、评估器和因子卡片。

每个新增因子必须同时包含：

1. `registry/factors/<factor_id>.yaml` 元数据；
2. `docs/factor-cards/<factor_id>.md` 因子卡片；
3. 可测试的实现；
4. 不使用未来数据的说明；
5. 至少一个单元测试。

提交前运行：

```bash
pytest
ruff check src tests
```

请勿提交 API Token、受限数据、未经授权的代码或仅展示最佳回测区间的结果。
