<template>
  <div class="study-mode">
    <div class="progress-bar">
      <div class="progress-info">
        <span>进度: {{ currentIndex + 1 }} / {{ cards.length }}</span>
        <span>正确: {{ correctCount }} | 错误: {{ wrongCount }}</span>
      </div>
      <el-progress :percentage="Math.round((currentIndex / cards.length) * 100)" :stroke-width="10" :show-text="false" />
    </div>

    <div class="study-card" :class="{ flipped: showAnswer }" @click="showAnswer = !showAnswer">
      <div class="card-flip-inner">
        <div class="card-front">
          <div class="card-label">问题</div>
          <div class="card-content">{{ currentCard.question }}</div>
          <div class="card-tip">点击查看答案</div>
        </div>
        <div class="card-back">
          <div class="card-label">答案</div>
          <div class="card-content">{{ currentCard.answer }}</div>
          <div class="card-tip">选择掌握程度</div>
        </div>
      </div>
    </div>

    <div class="control-buttons">
      <template v-if="!showAnswer">
        <el-button @click="showAnswer = true" type="primary" size="large">显示答案</el-button>
      </template>
      <template v-else>
        <el-button @click="markWrong" type="danger" size="large" :icon="Close">不会</el-button>
        <el-button @click="markHard" type="warning" size="large" :icon="QuestionFilled">困难</el-button>
        <el-button @click="markCorrect" type="success" size="large" :icon="Check">记住了</el-button>
      </template>
    </div>

    <div class="nav-buttons">
      <el-button @click="prevCard" :disabled="currentIndex === 0" :icon="ArrowLeft">上一张</el-button>
      <el-button @click="shuffleCards" :icon="Refresh">打乱</el-button>
      <el-button @click="nextCard" :disabled="currentIndex === cards.length - 1">
        下一张 <el-icon><ArrowRight /></el-icon>
      </el-button>
    </div>

    <el-dialog v-model="showComplete" title="🎉 学习完成!" width="400px" center>
      <div class="complete-content">
        <div class="trophy">🏆</div>
        <p>你已完成所有闪卡的学习!</p>
        <div class="stats">
          <div class="stat correct"><div class="num">{{ correctCount }}</div><div>记住了</div></div>
          <div class="stat wrong"><div class="num">{{ wrongCount }}</div><div>需复习</div></div>
        </div>
        <div class="rate">正确率: {{ Math.round((correctCount / cards.length) * 100) }}%</div>
      </div>
      <template #footer>
        <el-button @click="restartStudy">重新学习</el-button>
        <el-button type="primary" @click="$emit('complete')">返回列表</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ArrowLeft, ArrowRight, Check, Close, QuestionFilled, Refresh } from '@element-plus/icons-vue'

const props = defineProps({ cards: { type: Array, required: true } })
const emit = defineEmits(['complete'])

const shuffledCards = ref([...props.cards])
const currentIndex = ref(0)
const showAnswer = ref(false)
const correctCount = ref(0)
const wrongCount = ref(0)
const showComplete = ref(false)

const currentCard = computed(() => shuffledCards.value[currentIndex.value])

const nextCard = () => { if (currentIndex.value < shuffledCards.value.length - 1) { currentIndex.value++; showAnswer.value = false } }
const prevCard = () => { if (currentIndex.value > 0) { currentIndex.value--; showAnswer.value = false } }

const goNext = () => {
  if (currentIndex.value < shuffledCards.value.length - 1) { currentIndex.value++; showAnswer.value = false }
  else { showComplete.value = true }
}

const markCorrect = () => { correctCount.value++; goNext() }
const markWrong = () => { wrongCount.value++; goNext() }
const markHard = () => { correctCount.value++; goNext() }

const shuffleCards = () => {
  shuffledCards.value = [...shuffledCards.value].sort(() => Math.random() - 0.5)
  currentIndex.value = 0; showAnswer.value = false
}

const restartStudy = () => {
  currentIndex.value = 0; correctCount.value = 0; wrongCount.value = 0
  showAnswer.value = false; showComplete.value = false; shuffleCards()
}
</script>

<style scoped>
.study-mode { width: 100%; max-width: 600px; }
.progress-bar { margin-bottom: 24px; }
.progress-info { display: flex; justify-content: space-between; font-size: 14px; color: #606266; margin-bottom: 8px; }

.study-card { perspective: 1000px; height: 300px; cursor: pointer; margin-bottom: 24px; }
.card-flip-inner { position: relative; width: 100%; height: 100%; transition: transform 0.6s; transform-style: preserve-3d; }
.study-card.flipped .card-flip-inner { transform: rotateY(180deg); }
.card-front, .card-back {
  position: absolute; width: 100%; height: 100%; backface-visibility: hidden;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 24px; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}
.card-front { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
.card-back { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; transform: rotateY(180deg); }
.card-label { position: absolute; top: 12px; left: 16px; font-size: 14px; opacity: 0.8; }
.card-content { font-size: 18px; line-height: 1.6; text-align: center; max-height: 200px; overflow-y: auto; }
.card-tip { position: absolute; bottom: 12px; font-size: 12px; opacity: 0.6; }

.control-buttons { display: flex; justify-content: center; gap: 16px; margin-bottom: 20px; }
.nav-buttons { display: flex; justify-content: space-between; }

.complete-content { text-align: center; }
.trophy { font-size: 60px; margin-bottom: 16px; }
.stats { display: flex; justify-content: center; gap: 24px; margin: 16px 0; }
.stat { padding: 16px 24px; border-radius: 8px; }
.stat.correct { background: #e8f5e9; }
.stat.wrong { background: #ffebee; }
.stat .num { font-size: 28px; font-weight: bold; }
.stat.correct .num { color: #4caf50; }
.stat.wrong .num { color: #f44336; }
.rate { color: #606266; margin-top: 12px; }
</style>
