<template>
  <div class="page-card">
    <h3 class="page-title">文书模板</h3>
    <div class="toolbar">
      <el-radio-group v-model="query.category" @change="search">
        <el-radio-button value="">全部</el-radio-button>
        <el-radio-button v-for="c in TEMPLATE_CATEGORIES" :key="c" :value="c">{{ c }}</el-radio-button>
      </el-radio-group>
      <div class="spacer" />
      <el-radio-group v-model="viewMode" size="small">
        <el-radio-button value="card"><el-icon><Grid /></el-icon></el-radio-button>
        <el-radio-button value="table"><el-icon><List /></el-icon></el-radio-button>
      </el-radio-group>
    </div>

    <div v-loading="loading">
      <el-empty v-if="!records.length && !loading" description="暂无模板" />
      <el-row v-else-if="viewMode === 'card'" :gutter="16">
        <el-col v-for="t in records" :key="t.id" :xs="24" :sm="12" :md="8" :lg="6">
          <el-card shadow="hover" class="tpl-card">
            <div class="tpl-head">
              <el-icon :size="32" color="#1f4e79"><Document /></el-icon>
              <el-tag size="small" effect="plain">{{ t.category || '其他' }}</el-tag>
            </div>
            <div class="tpl-name" :title="t.name">{{ t.name }}</div>
            <div class="tpl-desc">{{ t.description || '暂无说明' }}</div>
            <div class="tpl-foot">
              <span class="count"><el-icon><Download /></el-icon>{{ t.downloadCount || 0 }} 次</span>
              <el-button type="primary" size="small" :icon="Download" @click="download(t)">下载</el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
      <el-table v-else :data="records" stripe border>
        <el-table-column prop="name" label="模板名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="description" label="说明" min-width="260" show-overflow-tooltip />
        <el-table-column prop="downloadCount" label="下载次数" width="100" align="center" />
        <el-table-column label="操作" width="110" align="center">
          <template #default="{ row }">
            <el-button type="primary" link :icon="Download" @click="download(row)">下载</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div class="pager">
      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.size"
        :total="total"
        :page-sizes="[8, 12, 24]"
        layout="total, sizes, prev, pager, next"
        background
        @current-change="load"
        @size-change="search"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Download } from '@element-plus/icons-vue'
import { listTemplates, templateDownloadUrl } from '@/api/public'
import { pageRecords, TEMPLATE_CATEGORIES } from '@/utils'

const viewMode = ref('card')
const query = reactive({ category: '', page: 1, size: 12 })
const records = ref([])
const total = ref(0)
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const res = pageRecords(await listTemplates(query))
    records.value = res.records
    total.value = res.total
  } finally {
    loading.value = false
  }
}

function search() {
  query.page = 1
  load()
}

function download(t) {
  window.open(templateDownloadUrl(t.id), '_blank')
  t.downloadCount = (t.downloadCount || 0) + 1
}

onMounted(load)
</script>

<style scoped>
.spacer {
  flex: 1;
}
.tpl-card {
  margin-bottom: 16px;
}
.tpl-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.tpl-name {
  font-weight: 600;
  font-size: 15px;
  margin: 10px 0 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.tpl-desc {
  font-size: 13px;
  color: #909399;
  height: 40px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.tpl-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
}
.count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #a8abb2;
}
</style>
