<script lang="ts">
import { createRouter, createWebHistory } from 'vue-router';
import Login from '../views/Login.vue';
import Chat from '../views/Chat.vue';
import Register from '../views/Register.vue';
import { useUserStore } from './useUserStore';
import Session from '../views/Session.vue';
import type { User } from './useUserStore'
import { useChatSession } from './useChatSession';
// backend URL
// const baseUrl = 'https://f382-2409-8a20-2a95-ce94-98dd-8ea1-dfd1-ec86.ngrok-free.app'
const baseUrl = 'http://localhost:8000'
// const baseUrl = 'https://f8c0-2409-8a20-2a95-ce94-f9fe-c6f7-b47a-425a.ngrok-free.app'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/',
            redirect: '/login',
        },
        {
            path: '/login',
            name: 'Login',
            component: Login,
        },
        {
            path: '/chat',
            name: 'Chat',
            component: Chat,
            children: [
                {
                    path: '',
                    name: 'NoneSession',
                    component: Session
                },
                {
                    path: ':id',
                    name: 'Session',
                    component: Session
                }
                
            ]
        },
        {
            path: '/register',
            name: 'Register',
            component: Register,
        }
    ],
});

router.beforeEach(async (to, from, next) => {
    const userStore = useUserStore()
    const user = userStore.user
    const { refreshDB, db } = useChatSession()
    await userStore.initialize()
    try {
        const token = await userStore.verify_token(user.token)
        user.token = token
        refreshDB(db)
    }
    catch (err) {
        user.status.logined = false
        user.token = ''
    }
    if (user.token) {
        user.status.logined = true
        next()
    }
    else {
        if (to.path !== '/login' && to.path !== '/register') {
            next('/login')
        }
        else {
            next()
        }
    }
})

export { baseUrl }
export default router
</script>