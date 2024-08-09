<script setup>
import { onMounted, watch } from 'vue'
import { Chart } from '@antv/g2'

const props = defineProps(['data', 'unit', 'title'])

const chart = new Chart({
  autoFit: true,
  height: 500
});

watch(() => props.data, (val) => {
  chart.changeData(val);
}, { deep: true })

onMounted(() => {
  chart
    .data(props.data)
    .encode('x', 'time')
    .encode('y', 'value')
    .scale('x', {
      type: 'time',
      range: [0, 1],
    })
    .scale('y', {
      domain: [0, 1000],
      nice: true,
    })
    .axis('y', {
      title: props.title,
      labelFormatter: (d) => d + props.unit
    })
    .axis('x', {
      title: '时间',
    });
  chart.line()
    .encode('shape', 'smooth')
    .legend('color', {})
    .legend('size', {});
  chart.render()
  const container = chart.getContainer(); // 获得挂载的容器
  document.getElementById('container').appendChild(container);
})

</script>


<template>
  <div>
    <div id="container"></div>
  </div>
</template>