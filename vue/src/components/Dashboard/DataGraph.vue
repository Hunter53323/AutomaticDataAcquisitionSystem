<script setup>
import { onMounted, watch, } from 'vue'
import { Chart } from '@antv/g2'

const props = defineProps(['data', 'unit', 'title'])

const chart = new Chart({
  autoFit: true,
  height: 300
});

watch(() => props.data, (val) => {
  chart
    .scale('x', {
      domain: [val[0].time, val[0].time + 20000],
      mask: 'HH:mm:ss.SSS ',
      type: 'time',
      range: [0, 1],
    })
    .scale('y', {
      domain: [0, Math.ceil(Math.max.apply(Math, val.map(item => { return item.val })) / 100 + 1) * 100],
      nice: true,
    })
    .changeData(val);
}, { deep: true })

onMounted(() => {
  chart
    .data(props.data)
    .encode('x', 'time')
    .encode('y', 'val')
    .encode('color', 'name')
    .scale('x', {
      type: 'time',
    })
    .scale('y', {
      domain: [0, 1000],
      nice: true,
    })
    .axis('y', {
      title: null,
      titleFontSize: 14,
      labelOpacity: 0.8,
      grid: true,
      gridStrokeOpacity: 0.5,
      labelFormatter: (d) => d,
      labelAlign: 'parallel'
    })
    .axis('x', {
      title: null,
      labelOpacity: 0.8,
      titleFontSize: 14,
      grid: true,
      gridStrokeOpacity: 0.5,
      labelAlign: 'parallel'
    })

  chart
    .line()
    .encode('size', 2)
    .encode('shape', 'smooth')
    .animate('update', { type: false })
    .legend('color', {
      position: 'right',
    });
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