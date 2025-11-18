<template>
  <div class="uploader-container">
    <div class="upload-box">
      <div class="upload-area" @dragover.prevent @drop.prevent="handleDrop">
        <input
          ref="fileInput"
          type="file"
          accept=".pdf,.docx,.pptx,.txt"
          @change="handleFileSelect"
          style="display: none"
        />
        
        <div v-if="!uploading" class="upload-content" @click="triggerFileSelect">
          <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="17 8 12 3 7 8"></polyline>
            <line x1="12" y1="3" x2="12" y2="15"></line>
          </svg>
          <p class="upload-text">点击或拖拽文件到此处上传</p>
          <p class="upload-hint">支持 PDF、DOCX、PPTX、TXT 格式</p>
        </div>

        <div v-else class="uploading-content">
          <div class="spinner"></div>
          <p>正在上传文件...</p>
        </div>
      </div>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import axios from 'axios'

export default {
  name: 'FileUploader',
  emits: ['upload-start', 'upload-success', 'upload-error'],
  setup(props, { emit }) {
    const fileInput = ref(null)
    const uploading = ref(false)
    const error = ref(null)

    const triggerFileSelect = () => {
      fileInput.value.click()
    }

    const handleFileSelect = (event) => {
      const file = event.target.files[0]
      if (file) {
        uploadFile(file)
      }
    }

    const handleDrop = (event) => {
      const file = event.dataTransfer.files[0]
      if (file) {
        uploadFile(file)
      }
    }

    const uploadFile = async (file) => {
      error.value = null
      uploading.value = true
      emit('upload-start')

      const formData = new FormData()
      formData.append('file', file)

      try {
        const response = await axios.post('/api/generate-flashcards-async', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })

        emit('upload-success', response.data)
      } catch (err) {
        const errorMessage = err.response?.data?.error || '上传失败，请重试'
        error.value = errorMessage
        emit('upload-error', errorMessage)
      } finally {
        uploading.value = false
        // 重置文件输入
        if (fileInput.value) {
          fileInput.value.value = ''
        }
      }
    }

    return {
      fileInput,
      uploading,
      error,
      triggerFileSelect,
      handleFileSelect,
      handleDrop
    }
  }
}
</script>

<style scoped>
.uploader-container {
  display: flex;
  justify-content: center;
}

.upload-box {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  width: 100%;
  max-width: 600px;
}

.upload-area {
  border: 3px dashed #cbd5e0;
  border-radius: 8px;
  padding: 3rem 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-area:hover {
  border-color: #667eea;
  background-color: #f7fafc;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.upload-icon {
  width: 64px;
  height: 64px;
  color: #667eea;
  margin-bottom: 1rem;
}

.upload-text {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 0.5rem;
}

.upload-hint {
  font-size: 0.9rem;
  color: #718096;
}

.uploading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-message {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #fed7d7;
  color: #c53030;
  border-radius: 6px;
  font-size: 0.9rem;
}
</style>
