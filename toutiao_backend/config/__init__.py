"""config 包初始化：统一加载后端目录下的 .env。

放在这里而不是 main.py，是为了保证任何入口（uvicorn、脚本、IDE 运行、
pytest）只要导入了 config.* 就会先加载 .env，不依赖导入顺序。
"""

from pathlib import Path

from dotenv import load_dotenv

# 锚定 toutiao_backend/ 目录，与启动时的工作目录无关
BACKEND_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BACKEND_DIR / ".env"

# override=False：系统环境变量（CI / 容器注入）优先于 .env
load_dotenv(dotenv_path=ENV_FILE, override=False)
