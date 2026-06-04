# 古籍标注平台 - 详细项目计划

> 版本: 1.0  
> 创建日期: 2026-06-04  
> 最后更新: 2026-06-04

---

## 1. 项目背景与目标

### 1.1 项目背景

古籍数字化过程中，OCR（光学字符识别）的质量直接影响后续研究工作的效率。现有OCR系统（MineRU、PaddleOCR）输出的古籍文本需要与权威版本（识典古籍）进行比对，以评估和改进OCR质量。

### 1.2 核心问题

1. **文件组织复杂** - 古籍文件分布在多个服务器目录，结构层次多
2. **匹配关系建立困难** - OCR文件与参考文本的对应关系需要人工确认
3. **质量评估可视化不足** - 相似度结果缺乏直观展示
4. **标注工作流程缺失** - 缺乏系统化的标注工具和流程

### 1.3 项目目标

建立一个完整的古籍标注平台，实现：
- 文件浏览与选择功能
- 基于Embedding的相似度计算与展示
- 左右对比的文本展示界面
- 用户标注功能与结果保存

---

## 2. 功能需求详细说明

### 2.1 文件浏览与选择模块

#### 2.1.1 功能描述

提供服务器目录树浏览功能，支持：
- 浏览指定目录下的古籍文件夹
- 展示文件层级结构（书籍→章节→段落）
- 支持多选文件进行批量处理

#### 2.1.2 目录结构

```
OCR文件目录:
├── mineru_ocr/
│   ├── 二十四史附清史稿_ocr/
│   │   ├── 隋书·[唐]魏征·(二十五史)·中华书局1973/
│   │   │   ├── 隋书·[唐]魏征·(二十五史)·中华书局1973.md
│   │   │   ├── images/
│   │   │   └── ...
│   │   └── ...
│   └── 十三经注疏_ocr/
│       └── ...
├── paddleocrvl_ocr/
│   ├── 二十四史附清史稿_ocr/
│   └── 十三经注疏_ocr/
    └── ...

参考文本目录:
├── shidianguji/
│   ├── 隋书/
│   │   ├── LS0013.zh-Hant.md
│   │   └── ...
│   └── ...
```

#### 2.1.3 界面设计

**左侧面板 - OCR文件选择器**
- 树形目录结构展示
- 支持展开/折叠
- 点击文件预览内容
- 搜索功能（按书名/章节名）

**右侧面板 - 参考文本选择器**
- 同样树形结构
- 可手动选择对应文件
- 或由系统自动推荐匹配

#### 2.1.4 API设计

```python
# 文件浏览API
GET /api/files/browse
    参数: path (目录路径)
    返回: 目录内容列表（文件/文件夹信息）

# 文件预览API
GET /api/files/preview
    参数: file_path (文件路径)
    返回: 文件内容（前N行或全部）

# 文件搜索API
GET /api/files/search
    参数: query (搜索关键词), path (搜索范围)
    返回: 匹配文件列表

# 自动匹配API
POST /api/files/match
    参数: ocr_file_path
    返回: 推荐的参考文本文件列表（基于文件名相似度）
```

### 2.2 Embedding相似度计算模块

#### 2.2.1 功能描述

调用Embedding服务，计算OCR文本与参考文本的相似度。

#### 2.2.2 技术细节

基于现有 `ocr_quality_evaluator.py` 的实现：

1. **文本预处理**
   - 清洗MineRU/PaddleOCR特殊标记
   - 清洗识典古籍HTML注释
   - 简繁转换统一为繁体

2. **文本分块**
   - 按段落和章节分块
   - 块大小: 350字符
   - 块重叠: 50字符

3. **Embedding获取**
   - API: `http://172.23.40.162:8180/v1/embeddings`
   - 批量处理: 32个文本块/批次
   - 超时时间: 60秒

4. **相似度计算**
   - 余弦相似度
   - 可选编辑距离补充

#### 2.2.3 Embedding缓存策略

**问题**: Embedding计算耗时，相同文件重复计算浪费资源。

**解决方案**: 
- 预计算常用文件的embedding
- 增量计算新文件的embedding
- 缓存到本地文件系统（JSON格式）

**缓存文件格式**:
```json
{
  "file_path": "/path/to/file.md",
  "file_hash": "sha256...",
  "chunks": [
    {
      "text": "文本内容...",
      "embedding": [0.123, 0.456, ...],
      "chapter": "章节名",
      "position": {"start": 0, "end": 350}
    }
  ],
  "computed_at": "2026-06-04T10:00:00"
}
```

#### 2.2.4 API设计

```python
# 计算相似度API
POST /api/similarity/compute
    参数: {
        ocr_file: "OCR文件路径",
        reference_file: "参考文件路径",
        options: {
            use_cache: true,
            chunk_size: 350,
            compute_mode: "full" | "incremental"
        }
    }
    返回: {
        task_id: "任务ID",
        status: "processing"
    }

# 获取计算状态API
GET /api/similarity/status/{task_id}
    返回: {
        status: "processing" | "completed" | "failed",
        progress: 75,
        result: null | {...}
    }

# 获取相似度结果API
GET /api/similarity/result/{task_id}
    返回: {
        overall_similarity: 0.85,
        chunks: [
            {
                ocr_text: "OCR文本块",
                ref_text: "参考文本块",
                similarity: 0.92,
                chapter: "章节名",
                position: {...}
            }
        ],
        chapter_stats: [...]
    }

# Embedding缓存管理API
GET /api/cache/list
    返回: 已缓存的文件列表

POST /api/cache/precompute
    参数: file_paths (文件路径列表)
    返回: 预计算任务ID

DELETE /api/cache/{file_path}
    返回: 删除状态
```

### 2.3 文本对比展示模块

#### 2.3.1 功能描述

左右并列展示OCR文本与参考文本，支持：
- 段落级别对齐
- 相似度可视化（颜色编码）
- 同步滚动
- 差异高亮

#### 2.3.2 界面设计

**主对比视图**

```
┌─────────────────────────────────────────────────────────────┐
│  [书籍名称] OCR vs 参考文本                                   │
│  整体相似度: 85.2%  |  低相似度块: 15/120                     │
├─────────────────────┬─────────────────────┬─────────────────┤
│   OCR文本           │   参考文本          │   相似度/操作    │
│                     │                     │                 │
│   (段落1)           │   (段落1)           │   92% [标注]    │
│   高祖上            │   高祖上            │                 │
│   隋书卷一...       │   隋书卷一...       │                 │
│                     │                     │                 │
│   [段落2]           │   [段落2]           │   65% [标注]    │
│   (高亮差异)        │   (高亮差异)        │   ⚠️ 低相似度   │
│                     │                     │                 │
├─────────────────────┴─────────────────────┴─────────────────┤
│  [< 上一章节]  [章节列表 ▼]  [下一章节 >]  [保存标注]        │
└─────────────────────────────────────────────────────────────┘
```

**相似度颜色编码**

| 相似度范围 | 颜色 | 说明 |
|-----------|------|------|
| ≥90% | 绿色 `#27ae60` | 高质量 |
| 80-90% | 黄绿 `#2ecc71` | 良好 |
| 70-80% | 黄色 `#f39c12` | 一般 |
| 60-70% | 橙色 `#e67e22` | 较差 |
| <60% | 红色 `#e74c3c` | 需改进 |

#### 2.3.3 技术实现

**前端组件**:
- 使用虚拟列表处理大文本
- Monaco Editor 或 CodeMirror 用于文本展示
- 自定义Diff组件用于差异高亮
- 同步滚动组件

**差异高亮算法**:
- 字符级Diff
- 词级Diff（中文按字）
- 支持忽略空格、标点差异

### 2.4 标注功能模块

#### 2.4.1 标注类型设计

| 标注类型 | 代码 | 说明 | 图标 |
|---------|------|------|------|
| 识别错误 | `error_char` | 字符被错误识别为其他字符 | 🔴 |
| 缺失内容 | `missing` | OCR遗漏的内容 | 📝 |
| 多余内容 | `extra` | OCR多识别的内容 | ➕ |
| 格式错误 | `format` | 标点、分段等格式问题 | ⚠️ |
| 模糊不清 | `unclear` | 原图模糊导致无法识别 | 🔍 |
| 其他问题 | `other` | 其他类型错误 | ❓ |

#### 2.4.2 标注操作流程

```
1. 点击 [标注] 按钮
   ↓
2. 弹出标注面板，展示当前段落
   ↓
3. 用户选择标注类型
   ↓
4. 在文本中选中错误区域
   ↓
5. 输入修正建议（可选）
   ↓
6. 添加备注说明（可选）
   ↓
7. 保存标注
```

#### 2.4.3 标注数据结构

```json
{
  "annotation_id": "ann_001",
  "file_pair": {
    "ocr_file": "/path/to/ocr.md",
    "reference_file": "/path/to/ref.md"
  },
  "chunk_info": {
    "chunk_index": 5,
    "chapter": "帝纪第一",
    "ocr_text": "高祖文皇帝...",
    "ref_text": "高祖文皇帝...",
    "similarity": 0.65
  },
  "annotation": {
    "type": "error_char",
    "ocr_position": {
      "start": 10,
      "end": 15
    },
    "original_text": "高祖文帝",
    "suggested_text": "高祖文皇帝",
    "confidence": 0.85,
    "note": "帝字漏印"
  },
  "annotator": {
    "user_id": "user_001",
    "name": "张三"
  },
  "created_at": "2026-06-04T10:30:00",
  "updated_at": "2026-06-04T10:30:00",
  "status": "draft" | "confirmed" | "reviewed"
}
```

#### 2.4.4 标注文件存储

**存储位置**: `/home/maxuejiao/guji/annotations/`

**文件命名**: `{ocr_file_hash}_annotations.json`

**目录结构**:
```
annotations/
├── mineru_ocr/
│   ├── 二十四史附清史稿_ocr/
│   │   ├── 隋书/
│   │   │   ├── ann_001.json  # 单个标注
│   │   │   ├── ann_002.json
│   │   │   └── summary.json  # 该书标注汇总
│   │   └── ...
│   └── 十三经注疏_ocr/
├── paddleocrvl_ocr/
└── stats.json  # 全局统计
```

#### 2.4.5 标注界面设计

**标注弹窗/侧边栏**

```
┌─────────────────────────────────────┐
│  新建标注                            │
├─────────────────────────────────────┤
│  标注类型: [识别错误 ▼]              │
│                                     │
│  OCR原文:                           │
│  "高祖文帝，姓杨氏..."               │
│  [选中区域高亮]                      │
│                                     │
│  参考文本:                           │
│  "高祖文皇帝，姓杨氏..."             │
│                                     │
│  修正建议:                           │
│  [输入框: "高祖文皇帝"]              │
│                                     │
│  备注:                              │
│  [输入框: "帝字漏印，应为皇帝"]      │
│                                     │
│  确信度: [85% ▼]                    │
│                                     │
│  [取消]  [保存草稿]  [确认并提交]    │
└─────────────────────────────────────┘
```

#### 2.4.6 API设计

```python
# 创建标注API
POST /api/annotations/create
    参数: {
        file_pair: {...},
        chunk_info: {...},
        annotation: {...}
    }
    返回: annotation_id

# 更新标注API
PUT /api/annotations/{annotation_id}
    参数: 更新的标注内容
    返回: 更新后的标注

# 删除标注API
DELETE /api/annotations/{annotation_id}
    返回: 删除状态

# 获取文件标注列表API
GET /api/annotations/list
    参数: file_path (可选), status (可选)
    返回: 标注列表

# 获取标注详情API
GET /api/annotations/{annotation_id}
    返回: 标注详情

# 标注统计API
GET /api/annotations/stats
    参数: scope (file/book/global)
    返回: 统计数据

# 导出标注API
GET /api/annotations/export
    参数: format (json/csv/xlsx), scope
    返回: 导出文件
```

---

## 3. 系统架构设计

### 3.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                         用户界面                             │
│  (React/Vue + Tailwind CSS + Monaco Editor)                 │
└─────────────────────────────────────────────────────────────┘
                              ↓↑ HTTP/REST API
┌─────────────────────────────────────────────────────────────┐
│                       后端服务                               │
│  (FastAPI + Uvicorn)                                        │
│  ┌──────────────┬──────────────┬──────────────────────┐    │
│  │  文件服务    │  相似度服务  │  标注服务             │    │
│  │  FileService │  SimService  │  AnnotationService   │    │
│  └──────────────┴──────────────┴──────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              ↓↑
┌─────────────────────────────────────────────────────────────┐
│                       外部依赖                               │
│  ┌──────────────┬──────────────┬──────────────────────┐    │
│  │  文件系统    │  Embedding   │  标注存储            │    │
│  │  (远程服务器)│  API服务     │  (JSON文件)          │    │
│  │  172.23.40.162│ 172.23.40.162│ 本地/远程           │    │
│  └──────────────┴──────────────┴──────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 后端模块划分

#### 3.2.1 目录结构

```
backend/
├── main.py                 # FastAPI主入口
├── config.py               # 配置管理
├── api/
│   ├── files.py           # 文件浏览API
│   ├── similarity.py      # 相似度计算API
│   ├── annotations.py     # 标注管理API
│   └── cache.py           # 缓存管理API
├── services/
│   ├── file_service.py    # 文件操作逻辑
│   ├── similarity_service.py  # 相似度计算逻辑
│   ├── annotation_service.py  # 标注管理逻辑
│   └── cache_service.py   # Embedding缓存逻辑
├── models/
│   ├── file.py            # 文件数据模型
│   ├── annotation.py      # 标注数据模型
│   └── similarity.py      # 相似度结果模型
├── utils/
│   ├── text_processor.py  # 文本处理工具
│   ├── embedding_client.py  # Embedding API客户端
│   └── file_utils.py      # 文件操作工具
└── requirements.txt       # Python依赖
```

#### 3.2.2 核心服务类

**FileService**
```python
class FileService:
    def browse_directory(path: str) -> List[FileInfo]
    def preview_file(file_path: str, lines: int = None) -> str
    def search_files(query: str, scope: str) -> List[FileInfo]
    def match_files(ocr_file: str) -> List[str]
    def get_file_tree(base_paths: List[str]) -> Dict
```

**SimilarityService**
```python
class SimilarityService:
    def compute_similarity(ocr_file: str, ref_file: str) -> TaskInfo
    def get_task_status(task_id: str) -> TaskStatus
    def get_result(task_id: str) -> SimilarityResult
    def precompute_embeddings(files: List[str]) -> TaskInfo
```

**AnnotationService**
```python
class AnnotationService:
    def create_annotation(data: AnnotationData) -> str
    def update_annotation(id: str, data: AnnotationData) -> Annotation
    def delete_annotation(id: str) -> bool
    def list_annotations(filter: AnnotationFilter) -> List[Annotation]
    def get_statistics(scope: str) -> AnnotationStats
    def export_annotations(format: str) -> str
```

### 3.3 前端模块划分

#### 3.3.1 目录结构（React示例）

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── FileBrowser/      # 文件浏览组件
│   │   │   ├── FileTree.tsx
│   │   │   ├── FilePreview.tsx
│   │   │   └── FileSelector.tsx
│   │   ├── TextCompare/      # 文本对比组件
│   │   │   ├── CompareView.tsx
│   │   │   ├── ChunkCard.tsx
│   │   │   ├── DiffHighlight.tsx
│   │   │   └── SyncScroll.tsx
│   │   ├── Annotation/       # 标注组件
│   │   │   ├── AnnotationPanel.tsx
│   │   │   ├── AnnotationEditor.tsx
│   │   │   ├── AnnotationList.tsx
│   │   │   └── AnnotationStats.tsx
│   │   └── Layout/           # 布局组件
│   │       ├── Header.tsx
│   │       ├── Sidebar.tsx
│   │       └── MainLayout.tsx
│   ├── pages/
│   │   ├── HomePage.tsx      # 主页
│   │   ├── ComparePage.tsx   # 对比页面
│   │   ├── AnnotationPage.tsx # 标注页面
│   │   └── StatsPage.tsx     # 统计页面
│   ├── services/
│   │   ├── api.ts            # API调用封装
│   │   ├── fileApi.ts        # 文件API
│   │   ├── similarityApi.ts  # 相似度API
│   │   └── annotationApi.ts  # 标注API
│   ├── utils/
│   │   ├── textUtils.ts      # 文本处理
│   │   ├── colorUtils.ts     # 颜色编码
│   │   └── storageUtils.ts   # 本地存储
│   ├── App.tsx
│   ├── index.tsx
│   └── types/                # TypeScript类型定义
└── package.json
```

---

## 4. 数据流设计

### 4.1 文件选择流程

```
用户操作                    前端                    后端                    文件系统
   │                         │                       │                       │
   │─ 浏览目录               │                       │                       │
   │                         │─ GET /api/files/browse│                       │
   │                         │                       │─ 读取目录内容         │
   │                         │                       │                       │─ 返回文件列表
   │                         │                       │←─────────────────────│
   │                         │← 目录列表             │                       │
   │← 展示目录树             │                       │                       │
   │                         │                       │                       │
   │─ 选择OCR文件            │                       │                       │
   │                         │─ GET /api/files/match │                       │
   │                         │                       │─ 计算文件名相似度     │
   │                         │                       │─ 搜索参考文件         │
   │                         │                       │                       │─ 返回匹配文件
   │                         │← 推荐参考文件         │                       │
   │← 展示推荐列表           │                       │                       │
   │                         │                       │                       │
   │─ 选择参考文件           │                       │                       │
   │                         │─ 计算相似度准备       │                       │
```

### 4.2 相似度计算流程

```
用户操作                    前端                    后端                    Embedding API
   │                         │                       │                       │
   │─ 开始计算               │                       │                       │
   │                         │─ POST /similarity/compute                      │
   │                         │                       │─ 创建任务             │
   │                         │← task_id              │                       │
   │                         │                       │                       │
   │                         │─ 定时查询状态         │                       │
   │                         │                       │─ 加载文件             │
   │                         │                       │─ 文本预处理           │
   │                         │                       │─ 文本分块             │
   │                         │                       │─ 检查缓存             │
   │                         │                       │                       │
   │                         │                       │─ POST /embeddings     │
   │                         │                       │                       │─ 返回embedding
   │                         │                       │←─────────────────────│
   │                         │                       │─ 计算相似度           │
   │                         │                       │─ 保存缓存             │
   │                         │                       │                       │
   │                         │─ GET /status          │                       │
   │                         │← progress: 100%       │                       │
   │                         │                       │                       │
   │                         │─ GET /result          │                       │
   │                         │← 相似度结果           │                       │
   │← 展示对比视图           │                       │                       │
```

### 4.3 标注保存流程

```
用户操作                    前端                    后端                    标注存储
   │                         │                       │                       │
   │─ 点击标注按钮           │                       │                       │
   │← 打开标注面板           │                       │                       │
   │                         │                       │                       │
   │─ 选择标注类型           │                       │                       │
   │─ 选中错误文本           │                       │                       │
   │─ 输入修正建议           │                       │                       │
   │─ 点击保存               │                       │                       │
   │                         │─ POST /annotations/create                     │
   │                         │                       │─ 验证数据             │
   │                         │                       │─ 生成ID               │
   │                         │                       │─ 保存JSON文件         │
   │                         │                       │                       │─ 写入成功
   │                         │                       │←─────────────────────│
   │                         │← annotation_id        │                       │
   │← 显示保存成功           │                       │                       │
```

---

## 5. 开发计划与里程碑

### 5.1 开发阶段划分

#### 第一阶段：基础架构搭建（1-2周）

**目标**: 建立项目基础结构，实现文件浏览功能

**任务清单**:
1. 创建项目目录结构
2. 配置后端FastAPI框架
3. 实现文件浏览API
4. 配置前端React/Vue框架
5. 实现文件树组件
6. 实现文件预览组件

**验收标准**:
- 后端服务可运行
- 前端可浏览服务器目录
- 文件预览功能正常

#### 第二阶段：相似度计算功能（2-3周）

**目标**: 实现Embedding相似度计算与展示

**任务清单**:
1. 集成现有 `ocr_quality_evaluator.py` 代码
2. 实现异步任务处理
3. 实现Embedding缓存机制
4. 实现相似度结果API
5. 实现文本对比展示组件
6. 实现相似度可视化（颜色编码）
7. 实现同步滚动和差异高亮

**验收标准**:
- 可成功计算相似度
- 计算进度实时展示
- 文本对比界面正常
- 相似度颜色编码正确

#### 第三阶段：标注功能（2-3周）

**目标**: 实现完整的标注工作流

**任务清单**:
1. 设计标注数据结构
2. 实现标注创建API
3. 实现标注管理API（更新/删除/查询）
4. 实现标注编辑界面
5. 实现标注列表展示
6. 实现标注统计功能
7. 实现标注导出功能

**验收标准**:
- 标注可正常创建
- 标注数据持久化
- 标注统计功能正常
- 标注导出功能正常

#### 第四阶段：优化与测试（1-2周）

**目标**: 性能优化、用户体验改进、测试

**任务清单**:
1. 性能优化（大文本处理）
2. 错误处理完善
3. 用户操作反馈优化
4. 单元测试编写
5. 集成测试
6. 用户验收测试

**验收标准**:
- 大文件加载流畅
- 错误提示友好
- 测试覆盖率 ≥70%
- 用户验收通过

#### 第五阶段：部署与文档（1周）

**目标**: 生产环境部署、文档完善

**任务清单**:
1. 生产环境配置
2. 部署脚本编写
3. 用户手册编写
4. API文档完善
5. 代码文档完善

**验收标准**:
- 生产环境正常运行
- 用户手册完整
- API文档完整

### 5.2 里程碑时间表

| 里程碑 | 目标日期 | 关键交付物 |
|--------|---------|-----------|
| M1: 基础架构 | 第2周末 | 文件浏览功能 |
| M2: 相似度功能 | 第5周末 | 对比展示功能 |
| M3: 标注功能 | 第8周末 | 完整标注功能 |
| M4: 优化测试 | 第10周末 | 测试通过版本 |
| M5: 部署上线 | 第11周末 | 生产环境部署 |

---

## 6. 技术决策与待定事项

### 6.1 技术决策

| 决策点 | 选择 | 理由 |
|--------|------|------|
| 后端框架 | FastAPI | 高性能、异步支持、自动API文档 |
| 前端框架 | React/Vue | 待选择，两者均可满足需求 |
| 文本对比组件 | Monaco Editor/CodeMirror | 待选择，Monaco更强大 |
| 文件存储格式 | JSON | 易于读写、人类可读 |
| 异步任务 | 后台线程 | 简单场景足够，复杂可升级Celery |

### 6.2 待定事项

1. **前端框架选择**: React vs Vue
   - React生态更丰富，组件库多
   - Vue上手更快，中文社区活跃
   - **建议**: React（生态优势）

2. **文本对比组件选择**: Monaco vs CodeMirror vs 自定义
   - Monaco功能强大，但体积大
   - CodeMirror轻量，中文支持好
   - 自定义灵活，但开发成本高
   - **建议**: Monaco（功能完整）

3. **数据库选择**: SQLite vs JSON文件
   - SQLite查询方便，但增加依赖
   - JSON文件简单，但查询性能差
   - **建议**: 先用JSON，后期可升级SQLite

4. **文件匹配策略**: 自动 vs 手动
   - 自动节省时间，但可能误配
   - 手动准确，但效率低
   - **建议**: 自动推荐 + 手动确认

---

## 7. 风险与应对

### 7.1 技术风险

| 风险 | 影响 | 应对策略 |
|------|------|---------|
| Embedding API不稳定 | 相似度计算失败 | 增加重试机制、降级方案 |
| 大文件加载慢 | 用户体验差 | 虚拟列表、分页加载 |
| 远程文件系统访问慢 | 文件浏览卡顿 | 本地缓存、异步加载 |
| 简繁转换错误 | 文本匹配失败 | 多种转换库对比、人工校验 |

### 7.2 业务风险

| 集险 | 影响 | 应对策略 |
|------|------|---------|
| 文件匹配关系错误 | 标注无效 | 提供手动修正功能 |
| 标注标准不一致 | 数据质量差 | 提供标注指南、审核机制 |
| 用户操作错误 | 数据丢失 | 草稿机制、版本控制 |

---

## 8. 附录

### 8.1 参考代码分析

基于 `ocr_quality_evaluator.py` 的关键实现：

1. **文本预处理** (TextPreprocessor类)
   - `clean_mineru_text()` - 清洗MineRU OCR输出
   - `clean_reference_text()` - 清洗识典古籍文本
   - `normalize_text()` - 简繁转换
   - `extract_chapters()` - 章节提取
   - `chunk_text()` - 文本分块

2. **Embedding客户端** (EmbeddingClient类)
   - `get_embedding()` - 单文本embedding
   - `get_embeddings_batch()` - 批量embedding

3. **相似度计算** (SimilarityCalculator类)
   - `cosine_similarity()` - 余弦相似度
   - `edit_distance()` - 编辑距离

4. **文本对齐** (TextAligner类)
   - `align_chunks()` - 文本块对齐
   - `_match_chapters()` - 章节匹配

### 8.2 API响应示例

**文件浏览响应**:
```json
{
  "path": "/home/maxuejiao/guji/mineru_ocr/二十四史附清史稿_ocr",
  "items": [
    {
      "name": "隋书·[唐]魏征·(二十五史)·中华书局1973",
      "type": "directory",
      "path": "/home/maxuejiao/guji/mineru_ocr/二十四史附清史稿_ocr/隋书·[唐]魏征·(二十五史)·中华书局1973",
      "file_count": 15
    },
    {
      "name": "汉书·[汉]班固·(二十五史)·中华书局1962.md",
      "type": "file",
      "path": "/home/maxuejiao/guji/mineru_ocr/二十四史附清史稿_ocr/汉书·[汉]班固·(二十五史)·中华书局1962.md",
      "size": 524288,
      "modified": "2026-05-20T10:00:00"
    }
  ]
}
```

**相似度结果响应**:
```json
{
  "task_id": "sim_task_001",
  "status": "completed",
  "result": {
    "overall_similarity": 0.852,
    "total_chunks": 120,
    "matched_chunks": 102,
    "chunks": [
      {
        "chunk_index": 0,
        "chapter": "帝纪第一",
        "ocr_text": "高祖文皇帝，姓杨氏...",
        "ref_text": "高祖文皇帝，姓杨氏...",
        "similarity": 0.92,
        "position": {"start": 0, "end": 350}
      }
    ],
    "chapter_stats": [
      {
        "chapter_name": "帝纪第一",
        "total_chunks": 10,
        "avg_similarity": 0.88,
        "low_similarity_count": 2
      }
    ]
  }
}
```

### 8.3 UI原型图（简化版）

**主页布局**:
```
┌──────────────────────────────────────────────────────────┐
│  古籍标注平台                           [用户名] [设置]  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │
│  │ 文件浏览│  │ 开始对比│  │ 标注管理│  │ 统计查看│    │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘    │
│                                                          │
│  快速开始:                                               │
│  [选择OCR文件] → [选择参考文件] → [开始对比] → [标注]   │
│                                                          │
│  最近工作:                                               │
│  - 隋书 OCR质量评估 (完成 85%)                          │
│  - 汉书 标注进行中 (标注 12/50)                         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

**文档结束**

> 本文档为项目计划初版，后续根据开发进展持续更新。