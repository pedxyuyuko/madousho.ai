## Task 2: Database 单例类实现 - Learnings

### 实现要点

1. **单例模式实现**
   - 使用 `__new__` 方法 + `_instance` 类属性
   - 提供 `get_instance()` 类方法作为标准访问入口
   - 确保 `db1 is db2` 返回 True

2. **类型注解最佳实践**
   - 使用 `Optional[T]` 而非 `T | None`（项目 Python 版本兼容性）
   - Generator 返回类型：`Generator[Session, None, None]`
   - `scoped_session` 需要泛型参数：`scoped_session[Session]`

3. **上下文管理器实现**
   - 使用 `@contextmanager` 装饰器
   - yield 前获取 session，yield 后 commit
   - except 块 rollback 并重新抛出异常
   - finally 块关闭 session

4. **SQLite 特定配置**
   - 检测 URL 是否以 "sqlite" 开头
   - 设置 `connect_args={"check_same_thread": False}`

5. **错误处理模式**
   - 捕获 `SQLAlchemyError`
   - 记录日志（包含 exc_info=True 显示堆栈）
   - rollback 后重新抛出异常

6. **包导出**
   - `__init__.py` 中导出 `Database` 类
   - 使用 `__all__` 明确公开 API

### 验证通过的方法
- ✓ `get_instance()` - 单例验证
- ✓ `init()` - 初始化数据库连接
- ✓ `is_initialized()` - 检查初始化状态
- ✓ `get_engine()` - 获取 Engine 实例
- ✓ `session()` - 上下文管理器，自动 commit/rollback
- ✓ `create_all_tables()` - 创建表结构
- ✓ `dispose()` - 清理连接

### Task 5: Database 测试实现 - Learnings

#### 测试要点

1. **单例模式测试**
   - 测试 `get_instance()` 返回相同实例
   - 测试 `__new__` 方法返回相同实例
   - 测试混合访问方式返回相同实例

2. **初始化状态测试**
   - 测试 `is_initialized()` 在 init 前后返回正确布尔值
   - 测试 `get_engine()` 返回 Engine 实例
   - 测试未初始化时 `get_engine()` 抛出 RuntimeError

3. **Session 管理器测试**
   - 测试 session() 上下文管理器正确 yield Session
   - 测试 session 自动 commit（使用 SQLAlchemy text() 执行原生 SQL 验证）
   - 测试 session 在异常时自动 rollback

4. **表创建测试**
   - 使用动态表名避免 SQLAlchemy 元数据缓存问题
   - 测试 `create_all_tables()` 创建表结构
   - 测试未初始化时抛出 RuntimeError

5. **清理测试**
   - 测试 `dispose()` 重置数据库状态

#### 测试隔离技术

- 使用 `@pytest.fixture(autouse=True)` 在每个测试前后重置单例状态
- 使用内存 SQLite (`sqlite:///:memory:`) 确保测试隔离
- 每个测试独立，不共享数据库状态

#### 注意事项

- SQLAlchemy 的 DeclarativeBase 会缓存类名和表名，避免在测试中使用相同的 `__tablename__`
- BaseModel 的 id 字段类型为 `Mapped[Optional[int]]`，测试中的模型需匹配此类型
- 使用 `type: ignore[no-untyped-def]` 抑制 pytest fixture 参数的类型检查警告

## Final Verification - All Tasks Complete

### Verification Results (All PASSED)

**Must Have Verification**:
- ✓ 单例模式验证通过
- ✓ 初始化验证通过
- ✓ Session 管理器验证通过
- ✓ 表结构创建验证通过

**Must NOT Have Verification**:
- ✓ 无连接池实现
- ✓ 无加密实现
- ✓ 无多数据库实现
- ✓ 无查询构建器实现
- ✓ 无自动重连实现

**Code Quality**:
- ✓ 无 TODO/FIXME/HACK
- ✓ 无 as any
- ✓ 无 @ts-ignore
- ✓ 无 console.log

**Evidence Files**:
- ✓ 所有证据文件存在

### Final Status
- 6/6 main tasks: COMPLETE
- 4/4 final verifications: COMPLETE
- 5/5 final checklist: COMPLETE
- 13/13 tests: PASSING

### Project Status
Database manager is production-ready and can be used across the codebase.
