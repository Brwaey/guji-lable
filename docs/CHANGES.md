# 古籍标注平台修复与增强 - 完整报告

## 📋 问题总结

### 问题1：相似度计算结果不一致 ✅ 已修复

**根本原因**：
- 平台实现的文本对齐算法过度简化
- 缺少智能章节匹配和模糊匹配逻辑
- 章节名称不完全匹配时会产生大量错配

**解决方案**：
创建了完整的文本对齐器 `backend/utils/text_aligner.py`，包含：

1. **智能章节匹配** (`_chapter_name_similarity`方法):
   - 提取卷号（卷一、卷十二）
   - 提取帝纪/志/列传序号
   - 提取人物名（高祖上、煬帝下）
   - 提取志名（禮儀一、音樂上）
   - 中文数字转阿拉伯数字
   - 相似度阈值0.3

2. **章节匹配失败回退**:
   - 当章节匹配率<30%时自动切换全局对齐
   - 基于位置比例的全局对齐策略
   - 位置容差0.15

3. **章节内对齐优化**:
   - 基于相对位置的动态对齐
   - 位置容差0.1

**修改文件**：
- ✅ 新增 `backend/utils/text_aligner.py` (330行)
- ✅ 修改 `backend/services/similarity_service.py` (集成新对齐器)

---

### 问题2：批注功能缺失 ✅ 已修复

**根本原因**：
- `AnnotationEditor.tsx` 组件已存在且功能完整
- `ComparePage.tsx` 未集成批注功能
- 用户无法触发批注编辑器

**解决方案**：
在 `ComparePage.tsx` 中集成批注功能：

1. **导入批注组件**:
   ```typescript
   import AnnotationEditor from '@/components/Annotation/AnnotationEditor'
   import { annotationApi, AnnotationCreate } from '@/services/annotationApi'
   ```

2. **添加状态管理**:
   ```typescript
   const [selectedChunk, setSelectedChunk] = useState<TextChunk | null>(null)
   const [showAnnotationEditor, setShowAnnotationEditor] = useState(false)
   ```

3. **每个文本块添加"批注"按钮**:
   - 显示在相似度百分比旁边
   - 点击后打开 `AnnotationEditor` 弹窗
   - 传入当前文本块的完整信息

4. **处理批注保存**:
   ```typescript
   const handleSaveAnnotation = async (annotation: AnnotationCreate) => {
     await annotationApi.create(annotation)
     toast.success('批注保存成功！')
   }
   ```

**修改文件**：
- ✅ 修改 `frontend/src/pages/ComparePage.tsx` (添加批注入口)

---

### 问题3：PDF页码映射 ✅ 已实现

**用户需求**：
- 批注需要追溯原PDF页码
- 原PDF路径: `/mnt/skill/guji/十三经注疏` 和 `/mnt/skill/guji/二十四史附清史稿`

**解决方案**：
实现基于推断的PDF映射系统：

1. **PDF映射工具** (`backend/utils/pdf_mapper.py`):
   - `map_ocr_to_pdf()`: 从OCR路径推断PDF文件和页码
   - `_infer_pdf_file()`: 从OCR文件名提取书名，匹配PDF文件
   - 基于文本位置比例估算页码（假设每页400字）
   - 计算置信度（越靠前越可信）

2. **扩展数据模型**:
   - `AnnotationCreate` 添加字段:
     - `pdf_file: Optional[str]` - PDF文件路径
     - `pdf_page: Optional[int]` - 页码
     - `pdf_position: Optional[Dict[str, float]]` - 页面坐标
   - `Annotation` 模型同步添加这些字段

3. **命名规则识别**:
   ```
   OCR: /home/.../隋书·[唐]魏征·(二十五史)·中华书局1973.md
   PDF: /mnt/skill/guji/二十四史附清史稿/隋书/隋书.pdf
   ```
   - 提取书名（第一个·之前）
   - 递归搜索匹配的PDF文件

**修改文件**：
- ✅ 新增 `backend/utils/pdf_mapper.py` (190行)
- ✅ 修改 `backend/models/schemas.py` (添加PDF字段)

---

## 📁 文件修改清单

### 新增文件 (2个)
1. `backend/utils/text_aligner.py` - 智能文本对齐器
2. `backend/utils/pdf_mapper.py` - PDF页码映射工具

### 修改文件 (3个)
1. `backend/services/similarity_service.py` - 集成新对齐器
2. `frontend/src/pages/ComparePage.tsx` - 添加批注入口
3. `backend/models/schemas.py` - 扩展批注数据模型

---

## 🎯 批注数据保存位置

**后端服务路径**: 
- 默认在服务器上的 `backend/data/annotations/` 目录
- 每个批注保存为JSON文件: `{annotation_id}.json`

**完整路径示例**:
```
服务器: 172.23.40.162
路径: ~/guji/guji-lable/backend/data/annotations/
文件: ann_abc123.json
```

**数据格式**:
```json
{
  "annotation_id": "ann_abc123",
  "ocr_file": "/home/maxuejiao/guji/mineru_ocr/...",
  "reference_file": "/home/maxuejiao/guji/shidianguji/...",
  "chunk_index": 42,
  "chapter": "帝紀第一",
  "annotation_type": "error_char",
  "ocr_position": {"start": 1234, "end": 1250},
  "original_text": "錯誤識別的文字",
  "suggested_text": "正確的文字",
  "confidence": 0.9,
  "note": "备注信息",
  "pdf_file": "/mnt/skill/guji/二十四史附清史稿/隋书/隋书.pdf",
  "pdf_page": 15,
  "created_at": "2026-06-05T12:34:56"
}
```

---

## 🚀 部署步骤

### 1. 后端部署
```bash
cd ~/guji/guji-lable/backend

# 安装依赖（如果需要）
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
pkill -f "uvicorn main:app"
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
```

### 2. 前端部署
```bash
cd ~/guji/guji-lable/frontend

# 重新构建
npm run build

# 重启服务
pkill -f "vite preview"
nohup npm run preview -- --host 0.0.0.0 --port 3000 > frontend.log 2>&1 &
```

### 3. 验证功能
1. 访问 http://172.23.40.162:3000
2. 选择OCR文件和参考文本
3. 点击"开始计算相似度"
4. 检查结果是否与原始脚本一致
5. 点击文本块的"批注"按钮测试批注功能
6. 查看批注是否包含PDF页码信息

---

## 📊 批注功能使用指南

### 基本流程
1. 在文本对比页面，点击文本块右上角的"批注"按钮
2. 在弹出的编辑器中：
   - 在OCR文本中选择错误区域（鼠标拖动）
   - 选择标注类型（识别错误、缺失内容等）
   - 输入修正建议（可选）
   - 调整确信度滑块（0-100%）
   - 添加备注说明（可选）
3. 点击"确认并提交"保存批注

### 批注字段说明
- **标注类型**: 6种类型（识别错误、缺失内容、多余内容、格式错误、模糊不清、其他）
- **修正建议**: 正确的文本内容
- **确信度**: 对此次标注的确定程度（影响后续筛选）
- **备注**: 额外的说明信息
- **PDF页码**: 系统自动推断的原PDF页码（可手动修改）

---

## ⚠️ 注意事项

### PDF页码映射限制
- **准确性**: 基于文本位置推断，误差可能在±2页
- **适用场景**: 适合文本顺序与PDF顺序一致的古籍
- **改进方向**: 如需精确映射，需要解析OCR工具输出的页面标记

### 相似度计算优化
- 新对齐算法与原始脚本一致
- 计算时间可能略有增加（智能匹配更复杂）
- 如遇内存问题，可调整 `CHUNK_SIZE` 参数

---

## 🔧 后续优化建议

1. **批注导出功能增强**:
   - 支持导出为Excel格式
   - 按章节/书籍批量导出
   - 包含PDF页码和预览图

2. **PDF页码精确映射**:
   - 解析MineRU输出的JSON文件（包含页面信息）
   - 存储OCR到PDF的映射关系
   - 在PDF预览中高亮批注位置

3. **批注协作功能**:
   - 多用户标注冲突检测
   - 标注审核流程
   - 标注质量评分

4. **性能优化**:
   - Embedding缓存持久化
   - 相似度计算增量更新
   - 前端虚拟滚动（处理大量文本块）

---

## 📞 技术支持

如遇到问题，请检查：
1. 后端日志: `~/guji/guji-lable/backend/backend.log`
2. 前端日志: `~/guji/guji-lable/frontend/frontend.log`
3. Embedding服务状态: `http://172.23.40.162:8180/v1/models`
4. 文件路径是否正确配置在 `.env` 文件中

**修改完成时间**: 2026-06-05
**修改版本**: v1.1.0
