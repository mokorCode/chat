<script scoped>
    import { createRouter, createWebHistory } from 'vue-router';
    import Login from '../views/Login.vue';
    import Chat from '../views/Chat.vue';
    import Register from '../views/Register.vue';
    import { useUserStore } from './useUserStore';
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
            },
            {
                path: '/register',
                name: 'Register',
                component: Register,
            }
        ],
    });
    
    router.beforeEach((to, from, next) => {
        const userStore = useUserStore()
        const token = userStore.token
        if (token){
            next()
        }
        else{
            next('/login')
        }
    })


    export default router

</script>