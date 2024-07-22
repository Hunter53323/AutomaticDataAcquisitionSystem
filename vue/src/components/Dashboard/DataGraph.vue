<script setup>
import { defineProps } from 'vue'
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
    .axis('y', { labelFormatter: (d) => d + '°C' });

  chart.line().encode('shape', 'smooth');
  chart.point().encode('shape', 'point').tooltip(false);
  chart.render();
}

</script>


<template>
  <el-button style="margin: 0 10px 0 0;" type="primary" @click="renderChart">Load</el-button>
  <div id="container"></div>
</template>