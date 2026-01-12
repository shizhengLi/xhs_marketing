# 环境变量配置说明

## 概述
本项目使用环境变量来管理敏感配置信息，特别是OpenAI API相关的配置。所有API密钥都通过环境变量加载，不直接硬编码在代码中。

## 环境变量配置

### 1. 创建.env文件
在`backend`目录下创建`.env`文件：

```bash
cd backend
cp .env.example .env
```

### 2. 配置OpenAI API密钥
编辑`.env`文件，设置以下环境变量：

```env
# AI Settings
OPENAI_API_KEY=your-actual-api-key-here
OPENAI_API_BASE=your-actual-api-base-here
AI_MODEL=gpt-3.5-turbo
```

### 3. 环境变量说明

| 变量名 | 说明 | 示例值 | 必填 |
|--------|------|--------|------|
| `OPENAI_API_KEY` | OpenAI API密钥 | `sk-xxxxx...` | 是 |
| `OPENAI_API_BASE` | OpenAI API基础URL | `https://api.openai.com/v1` | 是 |
| `AI_MODEL` | 使用的AI模型 | `gpt-3.5-turbo`, `gpt-4`, `gpt-5.1` | 否 |

## 使用方式

### 在Python代码中使用

#### 方式1：直接使用os.getenv()
```python
import os

api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")

if not api_key:
    raise ValueError("请设置 OPENAI_API_KEY 环境变量")
if not api_base:
    raise ValueError("请设置 OPENAI_API_BASE 环境变量")
```

#### 方式2：使用配置类
```python
from app.core.config import settings

api_key = settings.OPENAI_API_KEY
api_base = settings.OPENAI_API_BASE
model = settings.AI_MODEL
```

### 在OpenAI客户端中使用
```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE")
)
```

## 安全注意事项

1. **不要提交.env文件到git仓库**
   ```bash
   # 确保.gitignore包含.env
   echo ".env" >> .gitignore
   ```

2. **定期轮换API密钥**
   - 建议每3-6个月更换一次API密钥
   - 如果怀疑密钥泄露，立即更换

3. **使用不同环境的配置**
   - 开发环境：使用测试API密钥
   - 生产环境：使用正式API密钥
   - 设置不同的权限限制

4. **监控API使用情况**
   - 定期检查API调用记录
   - 设置使用限额和告警

## 测试配置

### 测试环境变量是否正确设置
```bash
# 在backend目录下运行
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('OPENAI_API_KEY:', os.getenv('OPENAI_API_KEY')[:10] + '...')
print('OPENAI_API_BASE:', os.getenv('OPENAI_API_BASE'))
"
```

### 测试OpenAI连接
```bash
python test_gpt.py
```

## 常见问题

### 1. 找不到API密钥
**错误信息**: `请设置 OPENAI_API_KEY 环境变量`

**解决方案**:
- 确认`.env`文件存在且在正确的目录
- 检查环境变量名称拼写是否正确
- 确认`.env`文件中有对应的内容

### 2. API调用失败
**错误信息**: `Unauthorized` 或 `Invalid API Key`

**解决方案**:
- 检查API密钥是否正确
- 确认API密钥未过期
- 检查API基础URL是否正确

### 3. 环境变量未生效
**可能原因**:
- `.env`文件位置不正确
- 未安装`python-dotenv`包
- IDE或运行时未正确加载环境变量

**解决方案**:
```bash
pip install python-dotenv
```

## 项目中的使用位置

### LLM服务 (`backend/app/services/llm_service.py`)
```python
import os
from openai import OpenAI

api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")

client = OpenAI(
    api_key=api_key,
    base_url=api_base
)
```

### 测试脚本 (`test_gpt.py`)
```python
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")

client = OpenAI(
    api_key=api_key,
    base_url=api_base
)
```

## 总结

通过使用环境变量管理API密钥，我们确保了：
- ✅ **安全性**: 敏感信息不暴露在代码中
- ✅ **灵活性**: 不同环境使用不同配置
- ✅ **可维护性**: 集中管理配置信息
- ✅ **标准化**: 遵循行业最佳实践