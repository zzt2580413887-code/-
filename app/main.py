import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 加载.env文件
try:
    from dotenv import load_dotenv
    # 获取项目根目录（main.py的上上上级目录）
    root_dir = Path(__file__).resolve().parents[2]
    env_path = root_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ 已加载环境变量配置文件: {env_path}")
    else:
        print(f"⚠ 未找到.env文件: {env_path}")
except ImportError:
    print("⚠ 未安装python-dotenv，将使用系统环境变量")
    print("  建议安装: pip install python-dotenv")

from backend.app.routers import (
    auth,
    chat,
    files,
    approval,
    analytics,
    documents,
    history,
    urban_gov_eval,
    knowledge_groups,
    knowledge_graph,
)

app = FastAPI(title="城市治理综合研究平台")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(files.router, prefix="/api/v1", tags=["files"])
app.include_router(approval.router, prefix="/api/v1", tags=["approval"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(documents.router, prefix="/api/v1", tags=["documents"])
app.include_router(history.router, prefix="/api/v1", tags=["history"])
app.include_router(urban_gov_eval.router, prefix="/api/v1", tags=["urban_gov_eval"])
app.include_router(knowledge_groups.router, prefix="/api/v1", tags=["knowledge_groups"])
app.include_router(knowledge_graph.router, prefix="/api/v1", tags=["knowledge_graph"])
if __name__ == "__main__":
    # Windows multiprocessing 支持
    import multiprocessing
    multiprocessing.freeze_support()

    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8890, reload=False)
