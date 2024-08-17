<script setup lang="ts">
import StatisticBox from '@/components/Dashboard/StatisticBox.vue'
// import ViewTitle from '@/components/ViewTitle.vue'
import DataGraph from '@/components/Dashboard/DataGraph.vue'
import FanControl from '@/components/Dashboard/FanControl.vue'
import TestControl from '@/components/Dashboard/TestControl.vue'
import CollectorBox from '@/components/Dashboard/CollectorBox.vue'
import ShowSelection from '@/components/ShowSelection.vue'
import { io } from 'socket.io-client'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useGlobalStore, useDashboardStore, useSettingsStore, useDBStore } from '@/stores/global'

const dataAll = ref({})
const global = useGlobalStore()
const dashboard = useDashboardStore()
const settings = useSettingsStore()
const db = useDBStore()
const socket = io(global.url)
const timeData = ref([])
const graphSelected = ref(["实际转速", "目标转速"])

const subObj = ((obj, arr) => {
  const res = {}
  try {
    arr.forEach(key => {
      if (obj[key]) {
        res[key] = obj[key]
      } else {
        res[key] = 0
      }
    })
  } catch (error) {
  }
  return res
})

const dataShow = reactive({
  FanDriver: {},
  TestDevice: {}
})
const paraShow = ref({})

watch(() => [dashboard.dataShowSelected, dashboard.paraShowSelected, dataAll.value],
  ([newDataSelected, newParaSelected, newData]) => {
    dataShow.FanDriver = subObj(newData, newDataSelected['FanDriver'])
    dataShow.TestDevice = subObj(newData, newDataSelected['TestDevice'])
    paraShow.value = subObj(newData, newParaSelected)
  }, { deep: true })


socket.on('data_from_device', data => {
  const timeRecv = Date.now()
  dataAll.value = data
  graphSelected.value.forEach(element => {
    timeData.value.push({
      time: timeRecv,
      val: data[element],
      name: element
    })
  })
  let timeMin = timeData.value.at(0).time
  let timeMax = timeData.value.at(-1).time
  if (timeMax - timeMin > 20000) {
    timeData.value = timeData.value.filter((val, index, arr) => val.time > timeMax - 10000);
  }
})

onMounted(() => {
  dashboard.initList()
  dashboard.initDeviceState()
  settings.initSettings()
  settings.updateConf()
  settings.updateDefined()
  db.updateMeta()
})

</script>

<template>
  <el-row :gutter="20">
    <el-col :span="12">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>被测设备控制</span>
          </div>
        </template>
        <FanControl :socket="socket" />
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>测试设备控制</span>
          </div>
        </template>
        <TestControl :socket="socket" />
      </el-card>
    </el-col>
  </el-row>

  <el-row :gutter="20">
    <el-col :span="24">
      <el-card shadow="hover">
        <DataGraph :data="timeData" unit="rpm" :title="graphSelected" />
      </el-card>
    </el-col>
  </el-row>

  <el-row :gutter="20">
    <el-col :span="16">
      <el-row>
        <el-col :span="24">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>测试设备数据</span>
                <ShowSelection :refList="dashboard.dataObjList['TestDevice']"
                  :selectedList="dashboard.dataShowSelected['TestDevice']"
                  @selected-change="(selectedList) => dashboard.dataShowSelected['TestDevice'] = selectedList" />
              </div>
            </template>
            <div class="statisticBox">
              <StatisticBox :contentObj="dataShow.TestDevice" :count="3" />
            </div>
          </el-card>
        </el-col>
      </el-row>
      <el-row style="margin: 0">
        <el-col :span="24">
          <el-card shadow="hover">
            <template #header>
              <div class="card-header">
                <span>被测设备数据</span>
                <ShowSelection :refList="dashboard.dataObjList['FanDriver']"
                  :selectedList="dashboard.dataShowSelected['FanDriver']"
                  @selected-change="(selectedList) => dashboard.dataShowSelected['FanDriver'] = selectedList" />
              </div>
            </template>
            <div class="statisticBox">
              <StatisticBox :contentObj="dataShow.FanDriver" :count="6" />
            </div>
          </el-card>
        </el-col>
      </el-row>

    </el-col>
    <el-col :span="8">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>参数</span>
            <ShowSelection :refList="dashboard.paraList" :selectedList="dashboard.paraShowSelected"
              @selected-change="(selectedList) => dashboard.paraShowSelected = selectedList" />
          </div>
        </template>
        <div class="statisticBox">
          <StatisticBox :contentObj="paraShow" :count="3" />
        </div>
      </el-card>
    </el-col>
  </el-row>



  <el-row :gutter="20">
    <el-col :span="24">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>采集配置</span>
          </div>
        </template>
        <collectorBox />
      </el-card>
    </el-col>
  </el-row>



</template>


<style scoped>
.el-card :deep(.el-card__header) {
  padding: 10px 20px;
}

.el-card :deep(.el-card__body) {
  padding: 10px 20px;
}

.el-card {
  height: 100%;
}

.el-row {
  margin: 0 0 10px 0;
}

.DataShowSelection {
  margin: 0 0 0 10px;
}
</style>
