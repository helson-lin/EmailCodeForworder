FROM python:3.12.3-slim-bullseye

# 添加作者标签
LABEL authors="helsonlin"

# 设置工作目录
WORKDIR /app

# 将当前目录内容复制到位于/app中的容器中
COPY main.py /app/
COPY requirements.txt /app/

# 安装requirements.txt中指定的任何所需程序包
# 安装依赖（如果有 requirements.txt）
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple


# 在容器启动时运行app.py
CMD ["python", "main.py"]
