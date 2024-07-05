<script setup>
import StatisticBox from '../components/StatisticBox.vue'
import ViewTitle from '../components/ViewTitle.vue'
</script>

<template>
  <ViewTitle viewTitle="DashBoard" />
  <StatisticBox class="statisticBox" />
</template>

<style scoped>
.statisticBox {
  margin: auto;
}
</style>
