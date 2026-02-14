<script setup lang="ts" name="Register">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/utils/useUserStore'
import { baseUrl } from '@/utils/useRouter.vue'
const userStore = useUserStore()
let password = ref('')
let username = ref('')
let ensurePassword = ref('')
let loading = ref(true)
const router = useRouter()
const token = userStore.user.token
const tokenLogin = userStore.tokenLogin
if ( token ) {
    tokenLogin(
        token,
        5000,
        () => {
            loading.value = false
            router.push('/chat')
        },
        () => {
            loading.value = false
        }
    )
}
else {
    loading.value = false
}
class RegisterData {
    username: string = ''
    password: string = ''
}
async function register(e: any) {
    loading.value = true
    if (password.value !== ensurePassword.value) {
        alert("两次密码并不一致，请重新输入")
        loading.value = false
        return
    }
    const data = new RegisterData()
    data.username = username.value
    data.password = password.value
    if ((data.password[0] == ' ') || (data.username[0] == ' ')) {
        alert("用户名和密码开头不能为空")
        loading.value = false
        return
    }
    const controller = new AbortController()
    const timeout = setTimeout(() => {
        controller.abort();
    }, 5000);
    try {
        const response = await fetch(`${baseUrl}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data),
            signal: controller.signal
        })
        const responseData = await response.json()
        if (response.ok) {
            const token = responseData.access_token
            localStorage.setItem('token', token)
            userStore.user.token = token
            router.push('/login')
        } else {
            alert(responseData.detail)
        }
    } catch (error) {
        alert(`
        ${error}
        连接超时或其他问题，可能是服务器过于卡顿，请稍后再试。
        `)
    } finally {
        loading.value = false
        clearTimeout(timeout)
    }
}
</script>
<template>
    <h1 style="margin: 0">
        Chat ~
    </h1>
    <h6 style="margin: 6px">
        注册以继续
    </h6>

    <el-form style="width: 300px; margin-top: 20px" label-position="top" @submit.prevent="register">
        <el-form-item label="用户名">
            <el-input :disabled="loading" id="username" autocomplete="username" v-model="username"
                placeholder="在这里输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="密码">
            <el-input :disabled="loading" id="password" autocomplete="current-password" v-model="password"
                type='password' placeholder="在这里输入密码"></el-input>
        </el-form-item>
        <el-form-item label="确认密码">
            <el-input :disabled="loading" id="ensurePassword" autocomplete="current-password" v-model="ensurePassword"
                type='password' placeholder="在这里输入密码"></el-input>
        </el-form-item>
        <el-form-item>
            <el-button :loading="loading" type="primary" style="width: 100%; margin-bottom: 1px;"
                native-type="submit">注册此账户</el-button>
        </el-form-item>

    </el-form>
</template>