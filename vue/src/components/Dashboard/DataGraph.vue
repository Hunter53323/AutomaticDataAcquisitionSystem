<script setup>
import { onMounted, watch, onUpdated, onUnmounted, ref } from 'vue'
import { Chart } from '@antv/g2'

const props = defineProps(['data', 'title', 'index'])

const sleep = (delay) => new Promise((resolve) => setTimeout(resolve, delay))

let chart
onMounted(() => {
  console.log("init")
  chart = new Chart({
    autoFit: true,
    height: 300
  });
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
      title: props.title,
      titleFontSize: 12,
      labelOpacity: 0.8,
      grid: true,
      gridStrokeOpacity: 0.5,
      labelFormatter: (d) => d,
      labelAlign: 'parallel'
    })
    .axis('x', {
      title: null,
      labelOpacity: 0.8,
      titleFontSize: 12,
      labelAutoRotate: true,
      grid: true,
      gridStrokeOpacity: 0.5,
      labelAlign: 'horizontal'
    })

  chart
    .line()
    .encode('size', 2)
    .encode('shape', 'smooth')
    .animate('update', { type: false })
    .legend('color');
  chart.render()
  const container = chart.getContainer(); // 获得挂载的容器
  document.getElementById('container' + props.index).appendChild(container);
})

onUnmounted(() => {
  chart.destroy()
})


watch(() => props.data, (val) => {
  chart
    .scale('x', {
      domain: [val[0].time, val[0].time + 20000],
      mask: 'mm:ss.SSS ',
      type: 'time',
      range: [0, 1],
    })
    .scale('y', {
      domain: [0, Math.ceil(Math.max.apply(Math, val.map(item => { return item.val })) / 10 + 1) * 10],
      nice: true,
    })
    .axis('y', {
      title: props.title,
      titleFontSize: 12,
      labelOpacity: 0.8,
      grid: true,
      gridStrokeOpacity: 0.5,
      labelFormatter: (d) => d,
      labelAlign: 'parallel'
    })
    .changeData(val);
}, { deep: true })

</script>


<template>
  <div>
    <div :id="'container' + props.index"></div>
  </div>
</template>