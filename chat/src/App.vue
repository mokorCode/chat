<script setup lang="ts">
import { ref } from 'vue';
import { RouterView } from 'vue-router'
  let logined = ref(false)
</script>

<template>
  <el-container id="main" v-if="logined" style="border: 5px solid">
    <el-header height="35px" class="color-header">
    </el-header>
    <el-container>
      <el-aside class="color-separate items" width="60px" style="border-right: 1px solid;">
        <el-container direction="vertical" style="height: 100%; align-items: center; justify-content: space-between; gap:16px; padding: 32px 10px 32px 10px;">
          <div style="display: flex; flex-direction: column; gap: 16px">
            <div class="item chat" style="display: flex; flex-direction: row; align-items: center; justify-content: center;"><el-icon size="20"><ChatDotRound /></el-icon></div>
            <div class="item friends" style="display: flex; flex-direction: row; align-items: center; justify-content: center;"><el-icon size="20"><User /></el-icon></div>
          </div>
          <div style="display: flex; flex-direction: column; gap: 16px">
            <div class="item star" style="display: flex; flex-direction: row; align-items: center; justify-content: center;"><el-icon size="20"><Star /></el-icon></div>
            <div class="item setting" style="display: flex; flex-direction: row; align-items: center; justify-content: center;"><el-icon size="20"><Setting /></el-icon></div>
          </div>
        </el-container>
      </el-aside>
      <el-aside class="color-background content" width="250px" style="border-right: 2px solid"></el-aside>
      <el-main class="color-separate main">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
  <el-container id="login" v-else="logined" style="background: #233; height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;">
      <RouterView />
  </el-container>
</template>

<style lang="scss">
</style>
