<template>
  <div class="flashcard-preview" :class="{ flipped: isFlipped }" @click="isFlipped = !isFlipped">
    <div class="card-flip-inner">
      <div class="card-front">
        <div class="card-number">#{{ index + 1 }}</div>
        <div class="card-text">{{ truncate(card.question, 80) }}</div>
        <div class="card-hint">点击翻转</div>
      </div>
      <div class="card-back">
        <div class="card-text">{{ truncate(card.answer, 80) }}</div>
        <div class="card-hint">点击翻转</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  card: { type: Object, required: true },
  index: { type: Number, required: true }
})

const isFlipped = ref(false)
const truncate = (text, len) => text.length <= len ? text : text.substring(0, len) + '...'
</script>

<style scoped>
.flashcard-preview { perspective: 1000px; height: 180px; cursor: pointer; }
.card-flip-inner {
  position: relative; width: 100%; height: 100%;
  transition: transform 0.6s; transform-style: preserve-3d;
}
.flashcard-preview.flipped .card-flip-inner { transform: rotateY(180deg); }
.card-front, .card-back {
  position: absolute; width: 100%; height: 100%;
  backface-visibility: hidden;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 16px; border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.card-front { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.card-back {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white; transform: rotateY(180deg);
}
.card-number { position: absolute; top: 8px; left: 12px; font-size: 12px; opacity: 0.7; }
.card-text { text-align: center; font-size: 14px; line-height: 1.5; }
.card-hint { position: absolute; bottom: 8px; font-size: 11px; opacity: 0.6; }
</style>
