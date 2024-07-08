<script setup>
import StatisticBox from '../components/StatisticBox.vue'
import ViewTitle from '../components/ViewTitle.vue'
import { ref } from 'vue'

const contentDataShow = ref([])
const contentParaShow = ref([])


fetch('http://127.0.0.1:5000/data', {
  method: 'GET',
}).then(res => {
  return res.json()
}).then(data => {
  contentDataShow.value = data
  console.log(contentDataShow)
})

fetch('http://127.0.0.1:5000/para', {
  method: 'GET',
}).then(res => {
  return res.json()
}).then(data => {
  contentParaShow.value = data
  console.log(contentParaShow)
})

fetch('http://127.0.0.1:5000/para', {
  method: 'POST',
}).then(res => {
  return res.json()
}).then(data => {
  contentParaShow.value = data
  console.log(contentParaShow)
})


</script>

<template>
  <ViewTitle viewTitle="DashBoard" />
  <StatisticBox class="statisticBox" :contentObj="contentDataShow" title="DataShow" />
  <StatisticBox class="statisticBox" :contentObj="contentParaShow" title="ParaShow" />
</template>

<style scoped>
.statisticBox {
  margin: auto;
}
</style>
