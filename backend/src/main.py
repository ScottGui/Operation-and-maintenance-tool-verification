# -*- coding: utf-8 -*-
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# 导入模型并创建数据库表
from backend.src.models import create_tables

# 导入路由
from backend.src.routes import auth, users, work_orders, assets, services, statistics


# 自定义 JSONResponse 类，确保中文正常显示
class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


app = FastAPI(
    title="公共数据运营授权运维平台 API",
    description="面向政务数据授权运营场景的智能运维管理系统",
    version="1.0.0",
    default_response_class=CustomJSONResponse
)

# 配置 CORS，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React 开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 应用启动时创建数据库表
@app.on_event("startup")
async def startup_event():
    create_tables()

# 注册路由
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(work_orders.router)
app.include_router(assets.router)
app.include_router(services.router)
app.include_router(statistics.router)


@app.get("/")
def read_root():
    return {"message": "欢迎使用 AI 原生 Web 应用 API"}


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
