<script name="Chat" setup lang="ts">
import { useChatSession } from '@/utils/useChatSession';
import { useUserStore } from '@/utils/useUserStore';
const userStore = useUserStore()
import { ref, computed, onMounted } from 'vue'
import type { Ref } from 'vue'
const user = userStore.user
const { sessionStatus, selectSession, initialize, getAllUsers } = useChatSession()
const users:Ref<string[]> = ref([])
onMounted(async () => {
    users.value = await getAllUsers(user.token)
})
setInterval(async () => {
    console.log('refresh all users')
    users.value = await getAllUsers(user.token)
}, 1000 * 10)
import { useRouter } from 'vue-router';
const router = useRouter()
function orderUsers(_users: string[]) {
    _users.sort((a, b) => b.charCodeAt(0) - a.charCodeAt(0))
    _users = _users.filter((v) => v != '$public-chat')
    _users.unshift('$public-chat')
    return _users
}

</script>
<template>
    <el-container id="main" style="min-height: 500px; display: flex; flex-direction: row; align-items: center; justify-content: center;">
        <el-container style="width: 85%; min-width: 450px; aspect-ratio: 2/1; flex-grow: 0;">
            <!--<el-header height="35px" class="color-header" style="border-radius: 16px 16px 0 0;">
            </el-header>-->
            <el-container>
                <el-aside class="color-separate items" width="60px" style="border-radius: 16px 16px 16px 16px; border-right: 1px solid;">
                    <el-container direction="vertical"
                        style="height: 100%; align-items: center; justify-content: space-between; gap:16px; padding: 32px 10px 32px 10px;">
                        <div style="display: flex; flex-direction: column; gap: 16px">
                            <div class="item chat"
                                style="display: flex; flex-direction: row; align-items: center; justify-content: center;">
                                <el-icon size="20">
                                    <ChatDotRound />
                                </el-icon>
                            </div>
                            <div class="item friends"
                                style="display: flex; flex-direction: row; align-items: center; justify-content: center;">
                                <el-icon size="20">
                                    <User />
                                </el-icon>
                            </div>
                        </div>
                        <div style="display: flex; flex-direction: column; gap: 16px">
                            <div class="item star"
                                style="display: flex; flex-direction: row; align-items: center; justify-content: center;">
                                <el-icon size="20">
                                    <Star />
                                </el-icon>
                            </div>
                            <div class="item setting"
                                style="display: flex; flex-direction: row; align-items: center; justify-content: center;">
                                <el-icon size="20">
                                    <Setting />
                                </el-icon>
                            </div>
                        </div>
                    </el-container>
                </el-aside>
                <el-aside class="color-background content" style="display: flex; flex-direction: column; width: 20%; border-radius: 16px 16px 16px 16px; border-right: 2px solid; padding: 16px 0 0 0;">
                    <div :class="(user == '$public-chat') ? 'sessions public-chat-container' : 'sessions'" v-for="(user, index) in orderUsers(users)" :key="index" style="height: 24px; display: flex; flex-direction: row; align-items: center; justify-content: center; margin-bottom: 8px; border-left: 4px solid white; user-select: none;">
                        <el-container @click="selectSession(user)">
                            <div :class="user == '$public-chat' ? 'public-chat-before' : ''" :size="24" :color="'#fff'" style="margin: 0 8px 0 8px;">
                                {{ user != '$public-chat' ? user.slice(0, 1).toUpperCase() : 'P'  }}
                            </div>
                            <span :class="user == '$public-chat' ? 'public-chat' : ''" style="text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">{{ user != '$public-chat' ? user : 'Public' }}</span>
                        </el-container>
                    </div>
                </el-aside>
                <el-main class="color-separate main" style="border-radius: 16px; padding: 0; min-width: 250px">
                    <RouterView />
                </el-main>
            </el-container>
        </el-container>
    </el-container>
</template>