<script setup lang="ts" name="Session">
import { useRoute } from 'vue-router';
import { onMounted, ref, computed, watch } from 'vue';
import type { Ref } from 'vue';
const route = useRoute()
const sessionId = computed(() => route.params.id)
console.log('sessionId', sessionId.value)
import { useChatSession } from '@/utils/useChatSession';
import { storeToRefs } from 'pinia';
import type { Session, Message } from '@/utils/useChatSession';
import { useUserStore } from '@/utils/useUserStore';
import type { User } from '@/utils/useUserStore'
import { nextTick } from 'vue';
const userStore = useUserStore()
const user = userStore.user
const allowSkipBottom = ref(false)
let refreshContentCountDown = 0
const { sessionStatus, selectSession, initialize, getAllUsers, sendSessionToDB, _getSession } = useChatSession()
const sessionNow: Ref<Session | null> = ref(null)
let contents = computed(() => sessionNow.value?.contents ?? [])
let inputMessage: Ref<string> = ref('')
const msgs = ref(null)
async function sendInputMessage() {
    if (!sessionNow.value) sessionNow.value = (await selectSession(sessionId.value as string)) || null
    if (!sessionNow.value) {
        alert('没有获取到会话，请重试')
        sessionNow.value = (await selectSession(sessionId.value as string)) || null
        return
    }
    console.log('session_now', sessionNow.value)
    const timeNow: string = String(Date.now())
    const messageContainer: Message = {
        time: timeNow,
        fromUser: user.username,
        id: sessionNow.value.contents.length ?? 0,
        content: inputMessage.value,
        type: 'msg-user'
    }
    sessionNow.value.contents.push(messageContainer)
    await sendSessionToDB(sessionNow.value)
    await update_contents()
    inputMessage.value = ''
    refreshContentCountDown = 0
    console.log(messageContainer)
    nextTick(() => {
        msgs.value.$el.scrollTop = msgs.value.$el.scrollHeight
    })

}
watch(() => contents.value[0]?.time, () => {
    if (contents.value[0]?.time) {
        nextTick(() => {
            msgs.value.$el.scrollTop = msgs.value.$el.scrollHeight
            allowSkipBottom.value = true
            nextTick(() => {
                if (msgs.value?.$el?.scrollTop + msgs.value?.$el.clientHeight > msgs.value?.$el?.scrollHeight - (msgs.value?.$el?.clientHeight)) {
                    allowSkipBottom.value = false
                    msgs.value.$el.scrollTop = msgs.value?.$el.scrollHeight
                }
        
            })
        })
    }
})

watch(() => sessionId.value, () => {
    console.log('reflesh sessionNow - sessionId was freshed')
    sessionNow.value = null
    allowSkipBottom.value = false
    update_contents()
    const msgsHeight = computed(() => msgs.value.$el.scrollHeight)
})

async function update_contents() {
    if (sessionId.value) {
        const new_contents = (await _getSession(user.token, user.username, sessionId.value as string))
        if (new_contents && sessionNow.value) {
            console.log('mergeContent')
            let mergeContent = [...sessionNow.value.contents, ...new_contents.contents]
            mergeContent = [...((new Map(mergeContent.map((c) => [Number(c.time), c]))).values())]
            mergeContent.sort((a, b) => Number(a.time) - Number(b.time))
            mergeContent.forEach((c, i) => {
                c.id = i
            })
            sessionNow.value.contents = mergeContent
            sendSessionToDB(sessionNow.value)
            nextTick(() => {
                if (msgs.value?.$el?.scrollTop + msgs.value?.$el.clientHeight > msgs.value?.$el?.scrollHeight - 10) {
                    allowSkipBottom.value = false
                }
            })
        }
        if (new_contents && !sessionNow.value) {
            sessionNow.value = new_contents
        }
    }
}



async function refreshContent() {
    if (refreshContentCountDown >= 1000) {
        await update_contents()
        refreshContentCountDown = 0
    }
    else refreshContentCountDown += 10
    setTimeout(() => {
        refreshContent()
    }, 10)
}
refreshContent()

function skipBottom() {
    if (msgs.value?.$el) {
        msgs.value.$el.scrollTop = msgs.value.$el.scrollHeight
        allowSkipBottom.value = false
    }
}





</script>
<template>
    <el-container v-if="!sessionId"
        style="user-select: none; pointer-events: none; height: 100%; width: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center;">
        <el-icon size="32">
            <close />
        </el-icon>
        <p style="color: gray;">没有选择会话</p>
    </el-container>
    <el-container v-else
        style="height: 100%; display: flex; flex-direction: column; align-items: stretch; justify-content: stretch;">
        <el-header
            style="user-select:none; height: 40px; border-radius: 16px 16px 0 0; border-bottom: 2px solid gray; display: flex; flex-direction: row; align-items: center;">
            <el-tooltip content="当会话名称超出长度时，按下 鼠标中键 进行浏览" placement="top">
                <span class="scrollbar"
                    style="font-size: 18px; font-weight: bold; overflow: scroll; overflow-y: hidden; white-space: nowrap; width: 100%;">{{
                        sessionId != '$public-chat' ? sessionId : '公开聊天室' }}</span>
            </el-tooltip>
        </el-header>
        <el-main ref="msgs" style="height: auto; padding: 0 12px 8px 12px;">
            <div style="position: relative; align-items: center; display: flex; flex-direction: row;"
                v-for="(content, index) in contents" :key="index">
                <div class='msg-user-avater' :size="24" :color="'#fff'" style="margin: 0 16px 0 8px;">
                    {{ content.fromUser.slice(0, 1).toUpperCase() }}
                </div>
                <div style="white-space: pre-wrap; word-break: break-all; width: 100%; margin: 16px 0 16px 0; display: flex; flex-direction: column;"
                    :class="`msg-user ${content.fromUser == user.username ? 'msg-user-right' : 'msg-user-left'}`">
                    <span class="msg-user-from-user" style="color: gray; font-size: 16px;"> {{ content.fromUser }}
                    </span>
                    <span class="msg-user-content"
                        style="background-color: #333; padding: 8px; border-radius: 8px; width: fit-content;"> {{
                            content.content }} </span>
                    <span class="msg-user-time" style="color: #444; font-size: 12px"> {{ new
                        Date(Number(content.time)).toLocaleString() }}
                    </span>
                </div>
            </div>
        </el-main>
        <el-footer class="session-input"
            style="position: relative; height: 60px; border-top: 4px solid gray; padding: 0;">
            <div @click="skipBottom" v-if="allowSkipBottom" class="allow-skip-bottom"
                style="user-select: none; background: #333; border-radius: 8px; translate:(-50%); padding: 8px 16px; position: absolute; left: 50%; bottom: 64px;">
                ↓
            </div>
            <el-input placeholder="我们来聊一聊..." v-model="inputMessage" style="height: 100%; width: 100%;"
                @keydown.enter.prevent="sendInputMessage"></el-input>
        </el-footer>
    </el-container>
</template>
