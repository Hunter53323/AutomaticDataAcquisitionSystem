<script setup>
import { defineProps, onMounted } from 'vue'
import { Chart } from '@antv/g2'

const props = defineProps(['data'])

const renderChart = () => {
  const chart = new Chart({
    container: 'container',
  });
  chart
    .data(props.data)
    .encode('x', 'time')
    .encode('y', 'value')
    .scale('x', {
      range: [0, 1],
    })
    .scale('y', {
      nice: true,
    })
    .axis('y', { labelFormatter: (d) => d});

  chart.line().encode('shape', 'smooth');
  chart.render();
}

onMounted(() => {
  setInterval(() => {
    renderChart()
  }, 1000)
})

</script>


<template>
  
  <div id="container"></div>
</template>