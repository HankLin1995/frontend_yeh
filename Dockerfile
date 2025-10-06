# 使用 Python 基礎映像
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt first for better caching
COPY requirements.txt ./

# Install the required Python packages
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 對於 Debian/Ubuntu 基礎映像
RUN apt-get update && apt-get install -y libzbar0

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py"]
