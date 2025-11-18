<template>
  <div class="task-status-container">
    <div class="status-card">
      <div class="status-header">
        <h2>任务状态</h2>
      </div>

      <div class="status-content">
        <div v-if="loading" class="status-loading">
          <div class="spinner-large"></div>
          <p class="status-text">{{ statusMessage }}</p>
        </div>

        <div v-else-if="error" class="status-error">
          <svg class="error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
          <p class="error-text">{{ error }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

export default {
  name: 'TaskStatus',
  props: {
    taskId: {
      type: String,
      required: true
    }
  },
  emits: ['task-complete', 'task-error'],
  setup(props, { emit }) {
    const loading = ref(true)
    const statusMessage = ref('等待处理...')
    const error = ref(null)
    let pollInterval = null

    const checkTaskStatus = async () => {
      try {
        const response = await axios.get(`/api/task-status/${props.taskId}`)
        const data = response.data

        if (data.state === 'PENDING') {
          statusMessage.value = '等待处理...'
        } else if (data.state === 'PROGRESS') {
          statusMessage.value = data.status || '处理中...'
        } else if (data.state === 'SUCCESS') {
          loading.value = false
          stopPolling()
          emit('task-complete', data.result)
        } else if (data.state === 'FAILURE') {
          loading.value = false
          error.value = data.status || '处理失败'
          stopPolling()
          emit('task-error', error.value)
        }
      } catch (err) {
        loading.value = false
        error.value = '无法获取任务状态'
        stopPolling()
        emit('task-error', error.value)
      }
    }

    const startPolling = () => {
      checkTaskStatus()
      pollInterval = setInterval(checkTaskStatus, 2000) // 每2秒轮询一次
    }

    const stopPolling = () => {
      if (pollInterval) {
        clearInterval(pollInterval)
        pollInterval = null
      }
    }

    onMounted(() => {
      startPolling()
    })

    onUnmounted(() => {
      stopPolling()
    })

    return {
      loading,
      statusMessage,
      error
    }
  }
}
</script>

<style scoped>
.task-status-container {
  display: flex;
  justify-content: center;
}

.status-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  width: 100%;
  max-width: 600px;
}

.status-header h2 {
  font-size: 1.5rem;
  color: #2d3748;
  margin-bottom: 1.5rem;
}

.status-content {
  min-height: 150px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.spinner-large {
  width: 60px;
  height: 60px;
  border: 5px solid #e2e8f0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.status-text {
  font-size: 1.1rem;
  color: #4a5568;
  font-weight: 500;
}

.status-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.error-icon {
  width: 60px;
  height: 60px;
  color: #e53e3e;
}

.error-text {
  font-size: 1rem;
  color: #c53030;
  text-align: center;
}
</style>
