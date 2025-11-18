<template>
  <div id="app">
    <header class="header">
      <h1>🎓 AI 闪卡生成器</h1>
      <p class="subtitle">上传文档，智能生成学习闪卡</p>
    </header>

    <main class="main-content">
      <FileUploader 
        @upload-start="handleUploadStart"
        @upload-success="handleUploadSuccess"
        @upload-error="handleUploadError"
      />

      <div v-if="taskId" class="task-section">
        <TaskStatus 
          :task-id="taskId"
          @task-complete="handleTaskComplete"
          @task-error="handleTaskError"
        />
      </div>

      <div v-if="flashcards.length > 0" class="flashcards-section">
        <FlashcardList :flashcards="flashcards" />
      </div>
    </main>

    <footer class="footer">
      <p>Built with Vue 3 + Flask + OpenAI</p>
    </footer>
  </div>
</template>

<script>
import { ref } from 'vue'
import FileUploader from './components/FileUploader.vue'
import TaskStatus from './components/TaskStatus.vue'
import FlashcardList from './components/FlashcardList.vue'

export default {
  name: 'App',
  components: {
    FileUploader,
    TaskStatus,
    FlashcardList
  },
  setup() {
    const taskId = ref(null)
    const flashcards = ref([])

    const handleUploadStart = () => {
      taskId.value = null
      flashcards.value = []
    }

    const handleUploadSuccess = (data) => {
      taskId.value = data.task_id
    }

    const handleUploadError = (error) => {
      console.error('Upload error:', error)
    }

    const handleTaskComplete = (result) => {
      flashcards.value = result
      taskId.value = null
    }

    const handleTaskError = (error) => {
      console.error('Task error:', error)
      taskId.value = null
    }

    return {
      taskId,
      flashcards,
      handleUploadStart,
      handleUploadSuccess,
      handleUploadError,
      handleTaskComplete,
      handleTaskError
    }
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  text-align: center;
  padding: 3rem 2rem;
  color: white;
}

.header h1 {
  font-size: 3rem;
  margin-bottom: 0.5rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
}

.main-content {
  flex: 1;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 0 2rem 2rem;
}

.task-section,
.flashcards-section {
  margin-top: 2rem;
}

.footer {
  text-align: center;
  padding: 2rem;
  color: white;
  opacity: 0.8;
  font-size: 0.9rem;
}
</style>
