<script setup lang="ts" name="Login">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/utils/useUserStore'
import { baseUrl } from '@/utils/useRouter.vue'
const userStore = useUserStore()
let password = ref('')
let username = ref('')
let loading = ref(true)
const router = useRouter()

let token: string | null = localStorage.getItem('token')
if (token == 'undefined'){
    token = ''
}
alert(token ? token : `No token found ${token}`)
const tokenLogin = userStore.tokenLogin

function jumpToRegister() {
    router.push('/register')
}

async function login() {
    loading.value = true
    const controller = new AbortController()
    const abort = setTimeout(() => {
        controller.abort()
    }, 5000)
    try {
        const response = await fetch(`${baseUrl}/login`, {
            'method': 'POST',
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': JSON.stringify({
                'username': username.value,
                'password': password.value
            }),
            'signal': controller.signal
        })
        if (response.ok){
            const data = await response.json()
            localStorage.setItem('token', data.access_token)
            userStore.user.token = data.access_token
            router.push('/chat')
        }
        else {
            alert('登录失败')
        }
    }
    catch {
      alert('连接超时')  
    }
    finally {
        loading.value = false
        clearTimeout(abort)
    }

}

if (token) {
    tokenLogin(token, 5000, () => { 
        loading.value = false
        router.push('/chat')
    }, () => { loading.value = false} )
}
else {
    loading.value = false
}
</script>
<template>
    <h1 style="margin: 0">
        Chat ~
    </h1>
    <h6 style="margin: 6px">
        请登录或注册以继续
    </h6>

    <el-form style="width: 300px; margin-top: 20px" label-position="top" @submit.prevent="login">
        <el-form-item label="用户名">
            <el-input :disabled="loading" id="username" autocomplete="username" v-model="username"
                placeholder="在这里输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码">
            <el-input :disabled="loading" id="password" autocomplete="current-password" v-model="password"
                type='password' placeholder="在这里输入密码"></el-input>
        </el-form-item>
        <el-form-item>
            <el-button :loading="loading" type="primary" style="width: 100%; margin-bottom: 1px;"
                native-type="submit">登录此账户</el-button>
        </el-form-item>
        <el-form-item>
            <el-button @click="jumpToRegister" :disabled="loading" type="text"
                style="width: 100%; text-align: center;">注册一个新账户？</el-button>
        </el-form-item>

    </el-form>
</template>