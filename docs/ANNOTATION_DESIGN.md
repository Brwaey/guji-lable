# 批注功能完整设计文档

## 🎯 用户场景分析

### 场景1：OCR识别错误
**情况**：OCR有字，但是识别错了
**操作**：
1. 点击文本块，右侧打开批注面板
2. 默认选中"识别错误"
3. 在OCR文本中拖动选择错误文字
4. 输入修正建议
5. 点击"保存批注"

### 场景2：OCR漏字（缺失内容）
**情况**：参考文本有，OCR没有
**操作**：
1. 点击文本块
2. 选择标注类型为"缺失内容"
3. **系统提示**："请在参考文本中选择缺失的内容"
4. 在参考文本中拖动选择缺失的文字
5. 点击"保存批注"

### 场景3：OCR多字
**情况**：OCR多了识别，参考文本没有
**操作**：
1. 点击文本块
2. 选择标注类型为"多余内容"
3. 在OCR文本中选择多余的文字
4. 点击"保存批注"

### 场景4：连续批注多个文本块
**情况**：同一章节有多处错误
**操作**：
1. 批注第一个文本块
2. 点击"下一块"按钮（或快捷键 →）
3. 继续批注
4. 批注面板保持打开，无需重复打开

### 场景5：查看和管理批注
**情况**：需要查看已批注的内容
**操作**：
1. 文本块有蓝色标记"已批注"
2. 点击"批注管理"菜单
3. 查看、筛选、导出批注
4. 批量操作（确认、删除）

---

## ✨ 核心功能改进

### 1. **全文批注模式** ✅
- ❌ 旧版：只显示前20个文本块
- ✅ 新版：分页显示所有文本块
- 每页可选：20/50/100/200条
- 支持首页/末页/上下页导航

### 2. **侧边栏批注面板** ✅
- ❌ 旧版：弹窗模式，每次都要关闭
- ✅ 新版：右侧固定侧边栏
  - 批注完自动清空，继续批注下一块
  - 上下块快捷导航
  - 不打断工作流

### 3. **双向文本选择** ✅
- ❌ 旧版：只能选择OCR文本
- ✅ 新版：根据标注类型智能切换
  - "识别错误" → 选择OCR文本
  - "缺失内容" → 选择参考文本（提示明确）
  - "多余内容" → 选择OCR文本

### 4. **批注状态可视化** ✅
- 文本块颜色标记：
  - 蓝色边框 = 已批注
  - 选中状态 = 粗边框高亮
  - 显示"已批注"徽章

### 5. **保存状态反馈** ✅
- 保存成功显示绿色提示
- "保存成功！继续批注"
- 不关闭面板，可继续批注

### 6. **批注管理页面** ✅
- 查看所有批注列表
- 筛选：类型、状态、搜索
- 批量操作：确认、删除
- 导出：JSON/CSV格式

---

## 🎨 UI/UX 设计细节

### 文本块颜色编码
```
相似度 >= 85%  → 绿色背景 (bg-sim-excellent)
相似度 70-85%  → 黄色背景 (bg-sim-medium)
相似度 < 70%   → 红色背景 (bg-sim-poor)
已批注         → 蓝色边框 + 蓝色背景 (border-blue-400 bg-blue-50)
选中           → 粗边框 + 浅蓝背景 (border-2 border-primary-500 bg-primary-50)
```

### 批注面板布局
```
┌─────────────────────────────┐
│ 快速批注              [×]   │ ← 标题栏
├─────────────────────────────┤
│ 文本块 #42                  │ ← 基本信息
│ 章节: 帝紀第一              │
│ 相似度: 92.5%               │
├─────────────────────────────┤
│ [🔴识别错误] [📝缺失内容]   │ ← 标注类型
│ [➕多余内容] [⚠️格式错误]   │
│ [🔍模糊不清] [❓其他问题]   │
├─────────────────────────────┤
│ ℹ️ 请在OCR文本中选择问题区域 │ ← 智能提示
├─────────────────────────────┤
│ OCR识别结果                 │ ← 可选择文本
│ [文本内容...]               │
│ ✓ 已选择: 错误文字          │
├─────────────────────────────┤
│ 修正建议: __________        │
│ 确信度: [====●==] 80%       │
│ 备注: ___________________   │
├─────────────────────────────┤
│ 已有批注 (2)                │ ← 历史批注
│ • 识别错误: "错字"          │
│ • 缺失内容: "缺字"          │
├─────────────────────────────┤
│ [✓ 保存成功！继续批注]      │ ← 状态反馈
│ [  保存批注  ]              │ ← 操作按钮
└─────────────────────────────┘
```

---

## 🔧 技术实现要点

### 1. 文本选择检测
```typescript
const handleTextSelection = () => {
  const selection = window.getSelection()
  if (selection && selection.toString()) {
    const selected = selection.toString()
    const element = document.getElementById(`ocr-text-${chunkIndex}`)
    const startIndex = element.textContent.indexOf(selected)
    setSelection({ text: selected, start: startIndex, end: startIndex + selected.length })
  }
}
```

### 2. 双向选择逻辑
```typescript
// 根据标注类型决定选择哪个文本
const requiresOcrSelection = ['error_char', 'extra', 'format', 'unclear'].includes(type)
const requiresRefSelection = type === 'missing'

// 智能提示
{annotationType === 'missing' ? (
  <p>请在参考文本中选择缺失的内容</p>
) : (
  <p>请在OCR文本中选择问题区域</p>
)}
```

### 3. 批注状态管理
```typescript
const [chunkAnnotations, setChunkAnnotations] = useState<Map<number, Annotation[]>>(new Map())

// 保存后更新本地状态
setChunkAnnotations(prev => {
  const newMap = new Map(prev)
  const annotations = newMap.get(chunkIndex) || []
  newMap.set(chunkIndex, [...annotations, newAnnotation])
  return newMap
})
```

### 4. 分页优化
```typescript
// 使用useMemo避免重复计算
const paginatedChunks = useMemo(() => {
  const start = (currentPage - 1) * pageSize
  const end = start + pageSize
  return result.chunks.slice(start, end)
}, [result, currentPage, pageSize])
```

---

## 📊 数据模型扩展

### AnnotationCreate
```typescript
{
  annotation_type: 'error_char' | 'missing' | 'extra' | 'format' | 'unclear' | 'other'
  original_text: string          // 选择的文本
  suggested_text?: string        // 修正建议
  confidence: number            // 0-1
  note?: string                 // 备注
  
  // 双向选择支持
  is_ref_selection?: boolean    // 是否选择参考文本
  ocr_position: { start: number, end: number }
  ref_position?: { start: number, end: number }
  
  // PDF映射
  pdf_file?: string
  pdf_page?: number
  pdf_position?: { x, y, width, height }
}
```

---

## 🚀 使用流程

### 批注工作流
```
1. 选择OCR文件 + 参考文本
2. 点击"开始计算相似度"
3. 等待计算完成（查看整体统计）
4. 点击低相似度文本块（红色/黄色）
5. 右侧打开批注面板
6. 选择标注类型
7. 选择问题文本（OCR或参考）
8. 输入修正建议 + 调整确信度
9. 点击"保存批注"
10. 点击"下一块"继续
11. 完成后到"批注管理"页面查看/导出
```

### 快捷键（建议实现）
```
→  : 下一块
←  : 上一块
Ctrl+S : 保存批注
Esc: 关闭批注面板
```

---

## ⚠️ 注意事项

### 文本选择限制
- 只能选择一个连续区域
- 跨段落选择会被分割
- 建议：大段错误分多次批注

### 批注保存时机
- 点击"保存批注"立即保存
- 未保存的选择切换文本块会丢失
- 建议：养成随时保存的习惯

### 缺失内容批注
- 必须在参考文本中选择
- OCR位置会被标记为{start:0, end:0}
- PDF页码基于参考文本位置推断

### 性能优化
- 大文件（>1000块）建议增加每页数量
- 虚拟滚动支持超大文件（待实现）
- Embedding缓存避免重复计算

---

## 📝 后续优化方向

### 1. 智能批注建议
- 根据相似度自动推荐批注类型
- 相似度<70%自动标记为"可能错误"
- 编辑距离分析推荐修正建议

### 2. 批量批注模式
- 选择多个文本块
- 应用相同的批注类型
- 一键确认所有低相似度块

### 3. 协作功能
- 多用户批注冲突检测
- 批注评论和讨论
- 审核流程管理

### 4. 数据可视化
- 批注热力图
- 错误类型分布图
- 章节质量报告

### 5. 导出增强
- Excel格式（带格式）
- PDF报告（带统计图表）
- API导出（第三方集成）

---

## 💡 最佳实践

### 批注策略
1. **优先处理低相似度块**（红色）
2. **关注高价值章节**（重点章节）
3. **批量处理相同错误**（格式问题）
4. **及时保存确认**（避免丢失）

### 质量控制
1. 设置确信度阈值（建议>=80%）
2. 添加详细备注说明
3. 定期审核批注
4. 导出备份批注数据

### 效率提升
1. 使用"下一块"快捷键
2. 预设常用修正建议
3. 批量操作类似错误
4. 分页大小调到100+

---

**设计完成时间**: 2026-06-05
**版本**: v2.0
**设计师**: Sisyphus (用户视角驱动设计)
