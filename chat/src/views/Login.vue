<script setup lang="ts" name="Login">
import { FALSE } from 'sass'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
let password = ref('')
let username = ref('')
let loading = ref(false)
const router = useRouter()
let token: string | null = localStorage.getItem('token')
if (token == 'undefined'){
    token = ''
}
alert(token ? token : 'No token found')

async function token_login(token: string) {
    loading.value = true
    const controller = new AbortController()
    const abort = setTimeout(() => {
        controller.abort()
    }, 5000)
    try {
        const response = await fetch('http://localhost:8000/token', {
            'method': 'POST',
            'headers': {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            'signal': controller.signal
        })
        if (response.ok){
            const data = await response.json()
            localStorage.setItem('token', data.access_token)
            alert(`
            自动登录成功
            new token: ${data.access_token}
            `)
            router.replace('/chat')
        }
        else {
            alert(`response: ${response.statusText},
            自动登录失败`)
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
        const response = await fetch('http://localhost:8000/login', {
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
    token_login(token)
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