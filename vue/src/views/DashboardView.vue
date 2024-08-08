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
import { UploadInstance, UploadProps, UploadRawFile, genFileId } from 'element-plus'
import { useGlobalStore, useDashboardStore } from '@/stores/global'
import { ElMessage } from 'element-plus'
import { select } from '@antv/g2'
import { c } from 'vite/dist/node/types.d-aGj9QkWt'
import { da } from 'element-plus/es/locale'

const dataAll = ref({})
const global = useGlobalStore()
const dashboard = useDashboardStore()
const socket = io(global.url)
const timeData = ref([])

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
    console.log(error)
  }
  return res
})

const dataShow = reactive({
  FanDriver: {},
  TestDevice: {}
})

watch(() => [dashboard.dataShowSelected, dataAll], ([newSelected, newData]) => {
  dataShow.FanDriver = subObj(newData, newSelected.FanDriver)
  dataShow.TestDevice = subObj(newData, newSelected.TestDevice)
}, { deep: true })


const getCurrentTime = () => {
  //获取当前时间并打印
  let dt = new Date()
  // let yy = dt.getFullYear();
  // let mm = dt.getMonth() + 1;
  // let dd = dt.getDate();
  let hh = dt.getHours();
  let mf = dt.getMinutes() < 10 ? '0' + dt.getMinutes() : dt.getMinutes();
  let ss = dt.getSeconds() < 10 ? '0' + dt.getSeconds() : dt.getSeconds();
  let ms = dt.getMilliseconds() < 10 ? '0' + dt.getMilliseconds() : dt.getMilliseconds();
  // return yy + '/' + mm + '/' + dd + ' ' + hh + ':' + mf + ':' + ss;
  return hh + ':' + mf + ':' + ss + '.' + ms;
}

socket.on('connection', data => {
  if (data.status == true) {
    dashboard.isConnected = true
  } else {
    dashboard.isConnected = false
  }
})

socket.on('data_from_device', data => {
  dataAll.value = data
  console.log(data)
  timeData.value.push({
    time: getCurrentTime(),
    value: data['actual_speed']
  })
  // console.log(timeData.value)
})

onMounted(() => {
  dashboard.initDataList()
})

</script>

<template>
  <!-- <ViewTitle viewTitle="DashBoard" /> -->
  <el-row :gutter="20">
    <el-col :span="12">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>测试设备控制</span>
          </div>
        </template>
        <FanControl :socket="socket" />
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>被测设备控制</span>
          </div>
        </template>
        <TestControl :socket="socket" />
      </el-card>
    </el-col>
  </el-row>

  <el-row :gutter="20">
    <el-col :span="12">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>测试设备数据</span>
            <ShowSelection :refList="dashboard.dataList.TestDevice"
              :selectedList="dashboard.dataShowSelected.TestDevice"
              @selected-change="(selectedList) => dashboard.dataShowSelected.TestDevice = selectedList" />
          </div>
        </template>
        <div class="statisticBox">
          <StatisticBox :contentObj="dataShow.TestDevice" :count="3" />
        </div>
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>测试设备数据</span>
            <ShowSelection :refList="dashboard.dataList.FanDriver" :selectedList="dashboard.dataShowSelected.FanDriver"
              @selected-change="(selectedList) => dashboard.dataShowSelected.FanDriver= selectedList" />
          </div>
        </template>
        <div class="statisticBox">
          <StatisticBox :contentObj="dataShow.FanDriver" :count="4" />
        </div>
      </el-card>
    </el-col>
  </el-row>

  <el-row :gutter="20">
    <el-col :span="12">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>采集配置</span>
          </div>
        </template>
        <collectorBox />
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card shadow="hover">
        <DataGraph :data="timeData" />
      </el-card>
    </el-col>
  </el-row>



</template>



<style scoped>
.el-card :deep() .el-card__header {
  padding: 15px 20px;
}

.card-header {
  font-size: larger;
}

.el-row {
  margin: 0 0 10px 0;
}

.DataShowSelection {
  margin: 0 0 0 10px;
}
</style>
