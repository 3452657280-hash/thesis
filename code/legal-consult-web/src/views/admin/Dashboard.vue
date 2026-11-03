<template>
  <div v-loading="loading">
    <el-row :gutter="16">
      <el-col v-for="c in cards" :key="c.label" :xs="12" :sm="8" :lg="4">
        <div class="stat-card">
          <div class="stat-icon" :style="{ background: c.color }">
            <el-icon :size="24"><component :is="c.icon" /></el-icon>
          </div>
          <div>
            <div class="stat-value">{{ c.value }}</div>
            <div class="stat-label">{{ c.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>
    <el-row :gutter="16">
      <el-col :xs="24" :lg="14">
        <div class="page-card chart-card">
          <h3 class="page-title">近14天提问趋势</h3>
          <div ref="lineRef" class="chart" />
        </div>
      </el-col>
      <el-col :xs="24" :lg="10">
        <div class="page-card chart-card">
          <h3 class="page-title">回答评分分布</h3>
          <div ref="barRef" class="chart" />
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getStats } from '@/api/admin'
import { formatMs } from '@/utils'

const loading = ref(false)
const stats = ref({})
const lineRef = ref()
const barRef = ref()
let lineChart = null
let barChart = null

const cards = computed(() => {
  const s = stats.value
  const avg = s.avgScore === null || s.avgScore === undefined ? '-' : Number(s.avgScore).toFixed(2)
  return [
    { label: '用户数', value: s.userCount ?? 0, icon: 'User', color: '#1f4e79' },
    { label: '律师数', value: s.lawyerCount ?? 0, icon: 'Avatar', color: '#2c7be5' },
    { label: '会话数', value: s.sessionCount ?? 0, icon: 'ChatLineSquare', color: '#00a2ae' },
    { label: '提问数', value: s.questionCount ?? 0, icon: 'QuestionFilled', color: '#67c23a' },
    { label: '平均评分', value: avg, icon: 'StarFilled', color: '#e6a23c' },
    { label: '平均响应耗时', value: formatMs(s.avgResponseMs === null || s.avgResponseMs === undefined ? null : Math.round(s.avgResponseMs)), icon: 'Timer', color: '#f56c6c' }
  ]
})

function last14Days(daily) {
  const map = new Map((daily || []).map((d) => [String(d.date).slice(0, 10), Number(d.count) || 0]))
  const dates = []
  const counts = []
  const pad = (n) => String(n).padStart(2, '0')
  for (let i = 13; i >= 0; i--) {
    const d = new Date()
    d.setDate(d.getDate() - i)
    const key = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
    dates.push(key.slice(5))
    counts.push(map.get(key) ?? 0)
  }
  return { dates, counts }
}

function render() {
  const s = stats.value
  const { dates, counts } = last14Days(s.dailyQuestions)
  lineChart = lineChart || echarts.init(lineRef.value)
  lineChart.setOption({
    color: ['#1f4e79'],
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 30, bottom: 30 },
    xAxis: { type: 'category', data: dates, boundaryGap: false },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        name: '提问数',
        type: 'line',
        data: counts,
        symbolSize: 7,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(31,78,121,0.35)' },
            { offset: 1, color: 'rgba(31,78,121,0.02)' }
          ])
        }
      }
    ]
  })

  const dist = new Map((s.scoreDistribution || []).map((d) => [Number(d.score), Number(d.count) || 0]))
  barChart = barChart || echarts.init(barRef.value)
  barChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 30, bottom: 30 },
    xAxis: { type: 'category', data: ['1星', '2星', '3星', '4星', '5星'] },
    yAxis: { type: 'value', minInterval: 1 },
    series: [
      {
        name: '评价数',
        type: 'bar',
        barWidth: '45%',
        data: [1, 2, 3, 4, 5].map((k) => dist.get(k) ?? 0),
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: (p) => ['#f56c6c', '#e6a23c', '#909399', '#62839f', '#1f4e79'][p.dataIndex]
        },
        label: { show: true, position: 'top' }
      }
    ]
  })
}

function resize() {
  lineChart?.resize()
  barChart?.resize()
}

async function load() {
  loading.value = true
  try {
    stats.value = (await getStats()) || {}
  } catch {
    stats.value = {}
  } finally {
    loading.value = false
    await nextTick()
    render()
  }
}

onMounted(() => {
  load()
  window.addEventListener('resize', resize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  lineChart?.dispose()
  barChart?.dispose()
})
</script>

<style scoped>
.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  background: #fff;
  border-radius: 8px;
  padding: 18px 16px;
  margin-bottom: 16px;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.06);
}
.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}
.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #303133;
}
.stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 2px;
}
.chart-card {
  margin-bottom: 16px;
}
.chart {
  height: 340px;
}
</style>
