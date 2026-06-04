# 古籍标注平台 (Guji Annotation Platform)

一个用于古籍OCR结果质量评估与标注的Web平台。

## 项目概述

本平台旨在解决古籍OCR（光学字符识别）结果的质量评估问题，通过embedding相似度对比和人工标注相结合的方式，提高古籍数字化质量。

### 核心功能

1. **文件浏览与选择** - 浏览服务器上的古籍OCR文件目录，支持分级选择
2. **相似度对比** - 基于embedding的OCR结果与参考文本（Ground Truth）相似度计算
3. **左右对比展示** - OCR结果与参考文本的并列展示
4. **标注功能** - 用户标注错误区域，支持多种标注类型
5. **结果保存** - 标注结果持久化存储到服务器

### 数据源

#### OCR文件目录
- `/home/maxuejiao/guji/mineru_ocr/二十四史附清史稿_ocr` - MineRU OCR结果
- `/home/maxuejiao/guji/mineru_ocr/十三经注疏_ocr` - MineRU OCR结果
- `/home/maxuejiao/guji/paddleocrvl_ocr/十三经注疏_ocr` - PaddleOCR结果
- `/home/maxuejiao/guji/paddleocrvl_ocr/二十四史附清史稿_ocr` - PaddleOCR结果

#### 参考文本目录（Ground Truth）
- `/home/maxuejiao/guji/shidianguji` - 识典古籍参考文本

#### Embedding服务
- API地址: `http://172.23.40.162:8180/v1`
- 模型: `embedding`

## 技术栈

### 后端
- **Python 3.8+**
- **FastAPI** - 高性能Web框架
- **Uvicorn** - ASGI服务器
- **NumPy** - 数值计算
- **Requests** - HTTP客户端（用于调用embedding API）

### 前端
- **React 18+** 或 **Vue 3+** (待确定)
- **Tailwind CSS** - 样式框架
- **Monaco Editor** 或类似组件 - 文本标注
- **Diff组件** - 文本对比展示

### 存储
- 文件系统存储标注结果（JSON格式）
- 可选：SQLite存储元数据

## 项目结构

```
guji-lable/
├── backend/                 # 后端服务
│   ├── api/                # API路由
│   ├── services/           # 业务逻辑
│   ├── models/             # 数据模型
│   ├── utils/              # 工具函数
│   └── config.py           # 配置文件
├── frontend/               # 前端应用
│   ├── src/
│   │   ├── components/    # React/Vue组件
│   │   ├── pages/         # 页面
│   │   ├── services/      # API调用
│   │   └── utils/         # 工具函数
│   └── public/
├── docs/                   # 文档
│   └── project-plan.md    # 详细项目计划
├── .gitignore
├── README.md
└── requirements.txt        # Python依赖
```

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+ (如果使用前端构建)
- 网络连接到内网服务器 (172.23.40.162)

### 后端安装

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 前端安装

```bash
cd frontend
npm install
```

### 运行服务

```bash
# 启动后端
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 启动前端开发服务器
cd frontend
npm run dev
```

## 标注工作流

1. **选择文件** - 从目录树中选择OCR文件和对应的参考文本
2. **计算相似度** - 系统自动计算embedding相似度
3. **查看对比** - 左右对比展示OCR结果与参考文本
4. **标注错误** - 高亮标注识别错误的区域
5. **保存结果** - 标注结果保存到服务器

## 标注类型

- **识别错误** - 字符被错误识别
- **缺失内容** - OCR遗漏的内容
- **多余内容** - OCR多识别的内容
- **格式错误** - 标点、分段等格式问题
- **其他** - 其他类型错误

## 配置说明

主要配置项在 `backend/config.py`:

```python
# Embedding服务配置
EMBEDDING_API_URL = "http://172.23.40.162:8180/v1"
EMBEDDING_MODEL = "embedding"

# 文件路径配置
OCR_BASE_PATHS = [
    "/home/maxuejiao/guji/mineru_ocr",
    "/home/maxuejiao/guji/paddleocrvl_ocr"
]
REFERENCE_BASE_PATH = "/home/maxuejiao/guji/shidianguji"

# 标注结果保存路径
ANNOTATION_OUTPUT_PATH = "/home/maxuejiao/guji/annotations"
```

## 开发计划

详见 [docs/project-plan.md](docs/project-plan.md)

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 许可证

待定

## 联系方式

项目维护者: 待定

## 致谢

- MineRU OCR团队
- PaddleOCR团队
- 识典古籍项目
