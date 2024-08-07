<script setup lang="ts">
import StatisticBox from '@/components/Dashboard/StatisticBox.vue'
import ViewTitle from '@/components/ViewTitle.vue'
import DataGraph from '@/components/Dashboard/DataGraph.vue'
import TestDeviceControl from '@/components/Dashboard/TestDeviceControl.vue'
import collectorBox from '@/components/Dashboard/CollectorBox.vue'
import { io } from 'socket.io-client'
import { onMounted, ref } from 'vue'
import { UploadInstance, UploadProps, UploadRawFile, genFileId } from 'element-plus'
import { useGlobalStore, useDashboardStore } from '@/stores/global'
import { ElMessage } from 'element-plus'

const contentDataShow = ref({})
const global = useGlobalStore()
const dashboard = useDashboardStore()
const socket = io(global.url)
const timeData = ref([])


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
  // delete data["breakdown"]
  contentDataShow.value = {}
  dashboard.dataShowSelected.forEach(element => {
    // if (element in data) {
    if (true) {
      contentDataShow.value[element] = data[element]
    }
  });

  // contentDataShow.value = data
  // console.log(contentDataShow.value)
  timeData.value.push({
    time: getCurrentTime(),
    value: data['actual_speed']
  })
  // console.log(timeData.value)
})

onMounted(() => {
  dashboard.updateDataList()
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
        <TestDeviceControl :socket="socket" />
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>被测设备控制</span>
          </div>
        </template>
        <TestDeviceControl :socket="socket" />
      </el-card>
    </el-col>
  </el-row>

  <el-row :gutter="20">
    <el-col :span="12">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>测试设备数据</span>
          </div>
        </template>
        <div class="statisticBox">
          <StatisticBox :contentObj="contentDataShow" />
        </div>
      </el-card>
    </el-col>
    <el-col :span="12">
      <el-card shadow="hover">
        <template #header>
          <div class="card-header">
            <span>测试设备数据</span>
          </div>
        </template>
        <div class="statisticBox">
          <StatisticBox :contentObj="contentDataShow" />
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
        <template #header>
          <div class="card-header">
            <span>被测设备控制</span>
          </div>
        </template>
      </el-card>
    </el-col>
  </el-row>
 

  <el-divider />
  <DataGraph :data="timeData" />

</template>



<style scoped>

.el-row{
  margin: 0 0 20px 0;
}



.divider {
  margin: 10px 0 10px 0;
}

.el-button {
  margin: 0 10px 0 0;
}
</style>
