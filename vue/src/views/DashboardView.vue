<script setup>
import StatisticBox from '../components/StatisticBox.vue'
import ViewTitle from '../components/ViewTitle.vue'
import { ref } from 'vue'

const content = ref([])

fetch('http://127.0.0.1:5000/data_test', {
  method: 'GET',
}).then(res => {
  return res.json()
}).then(data => {
  content.value = data
  console.log(content)
})

</script>

<template>
  <ViewTitle viewTitle="DashBoard" />
  <StatisticBox class="statisticBox" :contentObj="content" />
</template>

<style scoped>
.statisticBox {
  margin: auto;
}
</style>
