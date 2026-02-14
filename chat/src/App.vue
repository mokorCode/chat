<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { RouterView } from 'vue-router'
import { useUserStore } from './utils/useUserStore';
const userStore = useUserStore()
const logined = computed(() => userStore.logined)
onMounted(() => {
})
</script>

<template>
  <el-container id="login" style="background: #233; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;">
      <RouterView />
  </el-container>
</template>

<style lang="scss">
</style>
