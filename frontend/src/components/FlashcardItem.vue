<template>
  <el-card class="flashcard-item" shadow="hover">
    <div v-if="!editing" class="card-content">
      <div class="card-header">
        <el-tag type="info" size="small">#{{ index + 1 }}</el-tag>
        <el-button-group size="small">
          <el-button @click="startEdit" :icon="Edit" />
          <el-button @click="$emit('delete', index)" :icon="Delete" type="danger" />
        </el-button-group>
      </div>
      
      <div class="question">
        <div class="label">问题</div>
        <div class="text">{{ card.question }}</div>
      </div>
      
      <el-divider />
      
      <div class="answer">
        <div class="label">答案</div>
        <div class="text">{{ card.answer }}</div>
      </div>
    </div>
    
    <div v-else class="card-edit">
      <el-form label-position="top">
        <el-form-item label="问题">
          <el-input v-model="editQuestion" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="答案">
          <el-input v-model="editAnswer" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <div class="edit-actions">
        <el-button @click="cancelEdit" size="small">取消</el-button>
        <el-button @click="saveEdit" type="primary" size="small">保存</el-button>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'
import { Edit, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  card: { type: Object, required: true },
  index: { type: Number, required: true }
})

const emit = defineEmits(['update', 'delete'])

const editing = ref(false)
const editQuestion = ref('')
const editAnswer = ref('')

const startEdit = () => {
  editQuestion.value = props.card.question
  editAnswer.value = props.card.answer
  editing.value = true
}

const cancelEdit = () => { editing.value = false }

const saveEdit = () => {
  emit('update', props.index, { question: editQuestion.value, answer: editAnswer.value })
  editing.value = false
}
</script>

<style scoped>
.flashcard-item { transition: transform 0.3s; }
.flashcard-item:hover { transform: translateY(-2px); }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.label { font-size: 12px; color: #909399; margin-bottom: 4px; }
.text { color: #303133; line-height: 1.6; }
.edit-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 12px; }
</style>
