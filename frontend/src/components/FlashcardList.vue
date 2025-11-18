<template>
  <div class="flashcards-container">
    <div class="flashcards-header">
      <h2>🎉 生成完成！共 {{ flashcards.length }} 张闪卡</h2>
    </div>

    <div class="flashcards-grid">
      <div
        v-for="(card, index) in flashcards"
        :key="index"
        class="flashcard"
        :class="{ 'flipped': flippedCards.has(index) }"
        @click="toggleFlip(index)"
      >
        <div class="flashcard-inner">
          <div class="flashcard-front">
            <div class="card-number">闪卡 {{ index + 1 }}</div>
            <div class="card-content">
              <div class="question-label">问题</div>
              <p class="question-text">{{ card.question }}</p>
            </div>
            <div class="flip-hint">点击查看答案</div>
          </div>

          <div class="flashcard-back">
            <div class="card-number">闪卡 {{ index + 1 }}</div>
            <div class="card-content">
              <div class="answer-label">答案</div>
              <p class="answer-text">{{ card.answer }}</p>
            </div>
            <div class="flip-hint">点击返回问题</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'FlashcardList',
  props: {
    flashcards: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  setup() {
    const flippedCards = ref(new Set())

    const toggleFlip = (index) => {
      if (flippedCards.value.has(index)) {
        flippedCards.value.delete(index)
      } else {
        flippedCards.value.add(index)
      }
      // 触发响应式更新
      flippedCards.value = new Set(flippedCards.value)
    }

    return {
      flippedCards,
      toggleFlip
    }
  }
}
</script>

<style scoped>
.flashcards-container {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.flashcards-header {
  margin-bottom: 2rem;
}

.flashcards-header h2 {
  font-size: 1.8rem;
  color: #2d3748;
  text-align: center;
}

.flashcards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.flashcard {
  perspective: 1000px;
  cursor: pointer;
  height: 250px;
}

.flashcard-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.6s;
  transform-style: preserve-3d;
}

.flashcard.flipped .flashcard-inner {
  transform: rotateY(180deg);
}

.flashcard-front,
.flashcard-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.flashcard-front {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.flashcard-back {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  transform: rotateY(180deg);
}

.card-number {
  font-size: 0.85rem;
  opacity: 0.8;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.question-label,
.answer-label {
  font-size: 0.9rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  opacity: 0.9;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.question-text,
.answer-text {
  font-size: 1rem;
  line-height: 1.6;
  flex: 1;
}

.flip-hint {
  margin-top: 1rem;
  font-size: 0.8rem;
  opacity: 0.7;
  text-align: center;
  font-style: italic;
}

.flashcard:hover .flashcard-inner {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .flashcards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
