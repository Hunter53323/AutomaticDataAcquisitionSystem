<script setup lang="ts">
import { ref, onMounted, reactive, watch, computed } from 'vue'
// import SelectionBox from '@/components/settings/SelectionBox.vue';
import { useDBStore } from '@/stores/global';
import { useSettingsStore } from '@/stores/global';
import DBItemConf from '@/components/settings/DBColumnConf.vue';

interface Option {
  key: number
  label: string
  disabled: boolean
}

const db = useDBStore()
const settings = useSettingsStore()
const activeNames = ref(['1', '2'])
const value = ref([])
const data = ref<Option[]>([])

const generateData = (refList) => {
  const data: Option[] = []
  refList.forEach((item) => {
    data.push({
      key: item,
      label: item,
      disabled: false
    })
  })
  return data
}

watch(() => db.columns, (newVal) => {
  data.value = generateData(newVal)
}, { deep: true })
data.value = generateData(db.columns)

</script>

<template>
  <el-collapse v-model="activeNames" class="collapse-son">
    <el-collapse-item title="数据库显示" name="1" >
      <div class="transfer-item"> 
        <el-transfer class="selector" v-model="db.colunmsShowSelected" :button-texts="['隐藏', '显示']" :data="data"
          :titles="['隐藏数据', '显示数据']" />
        <!-- <SelectionBox class="selector" :ref-list="db.columns" :selected-list="db.colunmsShowSelected"
        @selectedChange="(selectedList) => db.colunmsShowSelected = selectedList" size="small" /> -->
      </div>
    </el-collapse-item>
    <el-collapse-item title="自定义存储" name="2">
      <DBItemConf />
    </el-collapse-item>
  </el-collapse>
</template>

<style scoped>
.transfer-item {
  display: flex;
  justify-content: center;
  align-items: center;
}

.selector {
  margin: 10px;
}

.selector :deep(.el-transfer-panel) {
  width: 450px;
}
</style>