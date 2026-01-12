# 小红书热点监控工具 - 后端

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行开发服务器

```bash
python main.py
```

或者使用uvicorn:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 环境变量

复制 `.env.example` 到 `.env` 并根据需要修改配置。