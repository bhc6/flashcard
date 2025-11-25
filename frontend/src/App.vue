<template>
  <div class="app">
    <!-- 顶部导航栏 -->
    <header class="header">
      <div class="header-content">
        <div class="logo">
          <el-icon :size="28"><Collection /></el-icon>
          <h1>Anki 闪卡生成器</h1>
        </div>
        <el-tag :type="apiStatus ? 'success' : 'danger'" effect="dark">
          API: {{ apiStatus ? '已连接' : '未连接' }}
        </el-tag>
      </div>
    </header>

    <main class="main-content">
      <el-row :gutter="24">
        <!-- 左侧：输入区域 -->
        <el-col :span="10">
          <el-card class="input-card">
            <template #header>
              <div class="card-header">
                <span>📥 导入内容</span>
                <el-radio-group v-model="inputMode" size="small">
                  <el-radio-button label="text">粘贴文本</el-radio-button>
                  <el-radio-button label="json">JSON数据</el-radio-button>
                </el-radio-group>
              </div>
            </template>

            <!-- 文本输入 -->
            <div v-if="inputMode === 'text'">
              <el-input
                v-model="inputText"
                type="textarea"
                :rows="10"
                placeholder="粘贴文本内容，格式：问题;答案&#10;例如：&#10;什么是Vue?;一个渐进式JavaScript框架"
              />
              <div class="text-actions">
                <span>分隔符:</span>
                <el-input v-model="textSeparator" style="width: 60px" />
                <el-button type="primary" @click="parseText" :loading="processing">解析</el-button>
                <el-button type="success" @click="generateFromText" :loading="processing">AI生成</el-button>
              </div>
            </div>

            <!-- JSON 输入 -->
            <div v-else>
              <el-input
                v-model="inputJson"
                type="textarea"
                :rows="10"
                placeholder='[{"question": "问题1", "answer": "答案1"}]'
              />
              <el-button type="primary" style="margin-top: 16px" @click="importJson" :loading="processing">
                导入 JSON
              </el-button>
            </div>
          </el-card>

          <!-- 操作面板 -->
          <el-card v-if="flashcards.length > 0" class="action-card">
            <template #header><span>⚙️ 操作</span></template>
            
            <div class="action-row">
              <span>共 {{ flashcards.length }} 张闪卡</span>
              <el-button-group>
                <el-button @click="addNewCard" type="success" :icon="Plus">添加</el-button>
                <el-button @click="enhanceCards" type="warning" :icon="MagicStick" :loading="enhancing">AI增强</el-button>
              </el-button-group>
            </div>

            <el-divider>导出</el-divider>
            
            <div class="export-buttons">
              <el-button @click="exportCards('json')" :icon="Download">JSON</el-button>
              <el-button @click="exportCards('txt')" :icon="Download">TXT</el-button>
              <el-button @click="exportCards('tsv')" :icon="Download">TSV</el-button>
              <el-button @click="exportCards('csv')" :icon="Download">CSV</el-button>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：闪卡展示 -->
        <el-col :span="14">
          <div class="view-header">
            <el-radio-group v-model="viewMode">
              <el-radio-button label="list"><el-icon><List /></el-icon> 列表</el-radio-button>
              <el-radio-button label="card"><el-icon><Postcard /></el-icon> 卡片</el-radio-button>
              <el-radio-button label="study"><el-icon><Reading /></el-icon> 学习</el-radio-button>
            </el-radio-group>
            
            <el-input v-model="searchQuery" placeholder="搜索闪卡..." :prefix-icon="Search" 
                      style="width: 200px" clearable />
          </div>

          <!-- 列表视图 -->
          <div v-if="viewMode === 'list'" class="cards-list">
            <el-empty v-if="filteredCards.length === 0" description="暂无闪卡" />
            <FlashcardItem
              v-for="(card, index) in filteredCards"
              :key="index"
              :card="card"
              :index="index"
              @update="updateCard"
              @delete="deleteCard"
            />
          </div>

          <!-- 卡片视图 -->
          <div v-else-if="viewMode === 'card'" class="cards-grid">
            <el-empty v-if="filteredCards.length === 0" description="暂无闪卡" />
            <FlashcardPreview
              v-for="(card, index) in filteredCards"
              :key="index"
              :card="card"
              :index="index"
            />
          </div>

          <!-- 学习模式 -->
          <div v-else class="study-container">
            <el-empty v-if="flashcards.length === 0" description="暂无闪卡" />
            <StudyMode v-else :cards="flashcards" @complete="viewMode = 'list'" />
          </div>
        </el-col>
      </el-row>
    </main>

    <!-- 添加弹窗 -->
    <el-dialog v-model="editDialogVisible" title="添加闪卡" width="500px">
      <el-form :model="editForm" label-width="60px">
        <el-form-item label="问题">
          <el-input v-model="editForm.question" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="答案">
          <el-input v-model="editForm.answer" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveNewCard">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Collection, Plus, MagicStick, Download, List, Postcard, Reading, Search } from '@element-plus/icons-vue'
import api from './api'
import FlashcardItem from './components/FlashcardItem.vue'
import FlashcardPreview from './components/FlashcardPreview.vue'
import StudyMode from './components/StudyMode.vue'

const apiStatus = ref(false)
const inputMode = ref('text')
const viewMode = ref('list')
const searchQuery = ref('')

const inputText = ref('')
const textSeparator = ref(';')
const inputJson = ref('')
const processing = ref(false)

const sessionId = ref('')
const flashcards = ref([])
const enhancing = ref(false)

const editDialogVisible = ref(false)
const editForm = ref({ question: '', answer: '' })

const filteredCards = computed(() => {
  if (!searchQuery.value) return flashcards.value
  const q = searchQuery.value.toLowerCase()
  return flashcards.value.filter(c => c.question.toLowerCase().includes(q) || c.answer.toLowerCase().includes(q))
})

onMounted(async () => {
  try {
    const result = await api.healthCheck()
    apiStatus.value = result.status === 'ok'
  } catch { apiStatus.value = false }
})

const parseText = async () => {
  if (!inputText.value.trim()) return ElMessage.warning('请输入文本')
  processing.value = true
  try {
    const result = await api.parseText(inputText.value, textSeparator.value)
    sessionId.value = result.session_id
    flashcards.value = result.flashcards
    ElMessage.success(`解析 ${flashcards.value.length} 张闪卡`)
  } catch (e) { ElMessage.error(e.message) }
  finally { processing.value = false }
}

const generateFromText = async () => {
  if (!inputText.value.trim()) return ElMessage.warning('请输入文本')
  processing.value = true
  try {
    const result = await api.generateFlashcards(sessionId.value, inputText.value)
    flashcards.value = result.flashcards
    ElMessage.success(`AI生成 ${flashcards.value.length} 张闪卡`)
  } catch (e) { ElMessage.error(e.message) }
  finally { processing.value = false }
}

const importJson = async () => {
  try {
    const data = JSON.parse(inputJson.value)
    const result = await api.importJson(data)
    sessionId.value = result.session_id
    const cards = await api.getFlashcards(sessionId.value)
    flashcards.value = cards.flashcards
    ElMessage.success(`导入 ${flashcards.value.length} 张闪卡`)
  } catch (e) { ElMessage.error('JSON格式错误: ' + e.message) }
}

const addNewCard = () => {
  editForm.value = { question: '', answer: '' }
  editDialogVisible.value = true
}

const saveNewCard = async () => {
  if (!editForm.value.question || !editForm.value.answer) return ElMessage.warning('请填写问题和答案')
  try {
    const result = await api.addFlashcard(sessionId.value, editForm.value.question, editForm.value.answer)
    sessionId.value = result.session_id
    flashcards.value.push({ ...editForm.value })
    editDialogVisible.value = false
    ElMessage.success('已添加')
  } catch (e) { ElMessage.error(e.message) }
}

const updateCard = async (index, card) => {
  try {
    await api.updateFlashcard(sessionId.value, index, card.question, card.answer)
    flashcards.value[index] = { ...card }
    ElMessage.success('已更新')
  } catch (e) { ElMessage.error(e.message) }
}

const deleteCard = async (index) => {
  try {
    await ElMessageBox.confirm('确定删除这张闪卡?', '确认', { type: 'warning' })
    await api.deleteFlashcard(sessionId.value, index)
    flashcards.value.splice(index, 1)
    ElMessage.success('已删除')
  } catch {}
}

const enhanceCards = async () => {
  if (!flashcards.value.length) return
  enhancing.value = true
  try {
    await api.enhanceFlashcards(sessionId.value)
    const data = await api.getFlashcards(sessionId.value)
    flashcards.value = data.flashcards
    ElMessage.success('AI增强完成')
  } catch (e) { ElMessage.error(e.message) }
  finally { enhancing.value = false }
}

const exportCards = async (format) => {
  if (!flashcards.value.length) return ElMessage.warning('没有可导出的闪卡')
  try {
    const blob = await api.exportFlashcards(sessionId.value, format)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `flashcards.${format}`
    a.click()
    URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (e) { ElMessage.error(e.message) }
}
</script>

<style scoped>
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
}
.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}
.logo h1 {
  font-size: 24px;
  font-weight: 600;
}
.main-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}
.input-card, .action-card {
  margin-bottom: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.text-actions {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.action-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.export-buttons {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.cards-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}
.study-container {
  display: flex;
  justify-content: center;
}
</style>
