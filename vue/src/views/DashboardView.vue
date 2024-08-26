<script setup lang="ts">
import StatisticBox from '@/components/Dashboard/StatisticBox.vue'
// import ViewTitle from '@/components/ViewTitle.vue'
import DataGraph from '@/components/Dashboard/DataGraph.vue'
import FanControl from '@/components/Dashboard/FanControl.vue'
import TestControl from '@/components/Dashboard/TestControl.vue'
import CollectorBox from '@/components/Dashboard/CollectorBox.vue'
import ShowSelection from '@/components/ShowSelection.vue'
import SelectionBox from '@/components/SelectionBox.vue'
import { io } from 'socket.io-client'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useGlobalStore, useDashboardStore, useSettingsStore, useDBStore } from '@/stores/global'

const dataAll = ref({})
const global = useGlobalStore()
const dashboard = useDashboardStore()
const settings = useSettingsStore()
const db = useDBStore()
const socket = io(global.url)
const timeData1 = ref([])
const timeData2 = ref([])
const graphClass1 = ref("转速")
const graphClass2 = ref("功率")
const graphSelected1 = ref(["实际转速", "目标转速"])
const graphSelected2 = ref([""])


const subObj = ((obj, arr) => {
  const res = {}
  try {
    arr.forEach(key => {
      if (obj[key]) {
        res[key] = obj[key]
      } else {
        res[key] = "NULL"
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
  graphSelected1.value.forEach(element => {
    timeData1.value.push({
      time: timeRecv,
      val: data[element],
      name: element
    })
  })
  graphSelected2.value.forEach(element => {
    timeData2.value.push({
      time: timeRecv,
      val: data[element],
      name: element
    })
  })
  let timeMin = timeData1.value.at(0).time
  let timeMax = timeData1.value.at(-1).time
  if (timeMax - timeMin > 20000) {
    timeData1.value = timeData1.value.filter((val, index, arr) => val.time > timeMax - 10000);
    timeData2.value = timeData2.value.filter((val, index, arr) => val.time > timeMax - 10000);
  }
})

socket.on('auto_collect_status', data => {
  dashboard.collectCount = data.remaining + data.success + data.fail
  dashboard.autoCollectStatus = data.status
  dashboard.remainCount = data.remaining
  dashboard.successCount = data.success
  dashboard.failCount = data.fail
  console.log(data.status)
})

socket.on('device_status', data => {
  // console.log(data)
  dashboard.isFanConnected = data.FanDriver['连接状态']
  dashboard.isFanRunning = data.FanDriver['运行状态']
  dashboard.isFanBreakDown = data.FanDriver['故障']
  dashboard.isTestConnected = data.TestDevice['连接状态']
  dashboard.isTestRunning = data.TestDevice['运行状态']
  dashboard.isTestBreakDown = data.TestDevice['故障']
  dashboard.autoCollectStatus = data.auto_collect_status.status
  dashboard.remainCount = data.auto_collect_status.remaining
  dashboard.successCount = data.auto_collect_status.success
  dashboard.failCount = data.auto_collect_status.fail
})


dashboard.initList()
dashboard.updateDeviceState()
settings.updateProtocol()
settings.updateConf()
settings.updateDefined()
settings.updateUser()
settings.updateSteady()
db.updateMeta()

</script>

<template>
  <el-row :gutter="10">
    <el-col :span="6">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>被测设备控制</span>
          </div>
        </template>
        <FanControl :socket="socket" />
      </el-card>
    </el-col>
    <el-col :span="6">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>测试设备控制</span>
          </div>
        </template>
        <TestControl :socket="socket" />
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span style="margin-right: 10px;">采集配置</span>
            <el-text class="collectorCount" type="primary">
              共{{ dashboard.collectCount }}条，剩余{{ dashboard.remainCount }}条，成功{{ dashboard.successCount }}条，
              失败{{ dashboard.failCount }}条
            </el-text>
          </div>
        </template>
        <collectorBox />
      </el-card>
    </el-col>
  </el-row>

  <el-row :gutter="10">
    <el-col :span="12">
      <el-card shadow="hover">
        <DataGraph :data="timeData1" :unit="global.getUnit(graphSelected1[0])" :title="graphSelected1" index="1" />
        <el-row class="graph-choice" :gutter="10">
          <el-col :span="8">
            <el-select v-model="graphClass1" placeholder="选择显示种类" style="width: 100%" size="small">
              <el-option v-for="value, key in dashboard.graphClass" :key="key" :label="key" :value="key" />
            </el-select>
          </el-col>
          <el-col :span="16">
            <SelectionBox :refList="dashboard.graphClass[graphClass1]" :selectedList="graphSelected1"
              @selected-change="(selectedList) => graphSelected1 = selectedList" size="small" />
          </el-col>
        </el-row>
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card shadow="hover">
        <DataGraph :data="timeData2" :unit="global.getUnit(graphSelected2[0])" :title="graphSelected2" index="2" />
        <el-row class="graph-choice" :gutter="10">
          <el-col :span="8">
            <el-select v-model="graphClass2" placeholder="选择显示种类" style="width: 100%" size="small">
              <el-option v-for="value, key in dashboard.graphClass" :key="key" :label="key" :value="key" />
            </el-select>
          </el-col>
          <el-col :span="16">
            <SelectionBox :refList="dashboard.graphClass[graphClass2]" :selectedList="graphSelected2"
              @selected-change="(selectedList) => graphSelected2 = selectedList" size="small" />
          </el-col>
        </el-row>
      </el-card>
    </el-col>
  </el-row>


  <el-row :gutter="10">
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
              <StatisticBox :contentObj="dataShow.TestDevice" :count="6" />
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



</template>


<style scoped>
.el-card :deep(.el-card__header) {
  padding: 10px 15px;
}

.el-card :deep(.el-card__body) {
  padding: 10px 15px 0;
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

.graph-choice {
  display: flex;
  align-items: center;
}
</style>
