<template>
  <div class="auth-page">
    <div class="intro">
      <div class="intro-inner">
        <el-icon :size="56"><ScaleIcon /></el-icon>
        <h1>法律咨询助手</h1>
        <p class="sub">—— 基于Coze智能体的法律咨询系统</p>
        <ul>
          <li><el-icon><ChatDotRound /></el-icon>智能体 7×24 小时在线解答法律疑问</li>
          <li><el-icon><Reading /></el-icon>常用法律法规条文便捷检索</li>
          <li><el-icon><Document /></el-icon>常用法律文书模板免费下载</li>
          <li><el-icon><Avatar /></el-icon>认证律师在线预约深度咨询</li>
        </ul>
      </div>
    </div>
    <div class="form-side">
      <div class="form-card">
        <h2>{{ title }}</h2>
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import ScaleIcon from './ScaleIcon.vue'

defineProps({ title: { type: String, default: '' } })
</script>

<style scoped>
.auth-page {
  display: flex;
  height: 100%;
  min-height: 560px;
}
.intro {
  flex: 1.2;
  background: linear-gradient(135deg, #1f4e79 0%, #2c6aa0 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
}
.intro-inner {
  max-width: 440px;
  padding: 40px;
}
.intro h1 {
  font-size: 34px;
  margin: 16px 0 4px;
  letter-spacing: 2px;
}
.sub {
  font-size: 16px;
  opacity: 0.85;
  margin: 0 0 32px;
}
.intro ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.intro li {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 14px 0;
  font-size: 15px;
  opacity: 0.92;
}
.form-side {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
}
.form-card {
  width: 380px;
  padding: 20px;
}
.form-card h2 {
  color: var(--law-blue);
  margin: 0 0 24px;
  font-size: 24px;
}
@media (max-width: 860px) {
  .intro {
    display: none;
  }
}
</style>
