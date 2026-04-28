import {createRouter , createWebHistory} from 'vue-router'
import loginView from '../views/Loginview.vue'
import chatView from '../views/Chatview.vue'
import aiChatView from '../views/AIChatView.vue'

const router = createRouter({
    history : createWebHistory(import.meta.env.BASE_URL),
    routes:[
        {
            path: '/',
            redirect: '/login'
        },
        {
            path: '/login',
            name: 'Login',
            component: loginView
        },
        {
            path: '/chat',
            name: 'Chat',
            component: chatView            
        },
        {
            path: '/ai',
            name: 'AIChat',
            component: aiChatView
        }
    ]
})
 
export default router
