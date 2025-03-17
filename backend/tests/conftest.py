import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
root_dir = str(Path(__file__).parent.parent)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir) 