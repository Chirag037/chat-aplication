import {createRouter , createWebHistory} from 'vue-router'
import loginView from '../views/Loginview.vue'
import chatView from '../views/Chatview.vue'

const router = createRouter({
    history : createWebHistory(import.meta.env.BASE_URL),
    routes:[
        {
            path: '/login',
            name: 'Login',
            component: loginView
        },
        {
            path: '/chat',
            name: 'Chat',
            component: chatView            
        }
    ]
})

export default router