<template>
  <div class="space-y-6">
    <div class="bg-white rounded-lg shadow-lg border border-gray-200 animate-fade-in">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200">
        <div class="flex items-center space-x-3">
          <h1 class="text-xl font-semibold text-gray-900">Messages</h1>
          <div class="flex items-center space-x-2">
            <div 
              class="w-2 h-2 rounded-full"
              :class="isConnected ? 'bg-green-500' : 'bg-red-500'"
            ></div>
            <span class="text-xs text-gray-500">
              {{ isConnected ? 'Connected' : 'Disconnected' }}
            </span>
          </div>
        </div>
        <button class="text-blue-600 hover:text-blue-700 transition-colors">
          <PaperAirplaneIcon class="w-5 h-5" />
        </button>
      </div>

      <!-- Following Users Section -->
      <div v-if="followingUsers.length > 0" class="p-4 border-b border-gray-200">
        <h3 class="text-sm font-medium text-gray-700 mb-3">People you follow</h3>
        <div class="flex space-x-3 overflow-x-auto pb-2">
          <div 
            v-for="user in followingUsers" 
            :key="user.id"
            @click="openChat(user)"
            class="flex-shrink-0 flex flex-col items-center cursor-pointer group"
          >
            <div class="w-12 h-12 rounded-full overflow-hidden mb-2 border-2 border-transparent group-hover:border-blue-500 transition-colors">
              <img 
                v-if="user.profile_picture" 
                :src="`http://localhost:5001${user.profile_picture}`" 
                :alt="user.username"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full bg-gray-300 flex items-center justify-center">
                <UserIcon class="w-6 h-6 text-gray-600" />
              </div>
            </div>
            <span class="text-xs text-gray-600 group-hover:text-blue-600 transition-colors truncate max-w-12">
              {{ user.username }}
            </span>
          </div>
        </div>
      </div>

      <!-- Conversations List -->
      <div v-if="loading" class="text-center py-12">
        <div class="spinner w-12 h-12 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading conversations...</p>
      </div>

      <div v-else-if="conversations.length === 0" class="text-center py-12">
        <div class="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <ChatBubbleLeftRightIcon class="w-12 h-12 text-gray-400" />
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No messages yet</h3>
        <p class="text-gray-600">Start a conversation with someone you follow</p>
      </div>

      <div v-else class="divide-y divide-gray-200">
        <div 
          v-for="conversation in conversations" 
          :key="conversation.partner.id"
          @click="openChat(conversation.partner)"
          class="flex items-center p-4 hover:bg-gray-50 cursor-pointer transition-colors"
        >
          <!-- Profile Picture -->
          <div class="w-12 h-12 rounded-full overflow-hidden mr-4">
            <img 
              v-if="conversation.partner.profile_picture" 
              :src="`http://localhost:5001${conversation.partner.profile_picture}`" 
              :alt="conversation.partner.username"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full bg-gray-300 flex items-center justify-center">
              <UserIcon class="w-6 h-6 text-gray-600" />
            </div>
          </div>

          <!-- Conversation Info -->
          <div class="flex-1 min-w-0">
            <div class="flex items-center justify-between">
              <h3 class="font-medium text-gray-900 truncate">{{ conversation.partner.username }}</h3>
              <p class="text-sm text-gray-500">{{ formatTimeAgo(conversation.last_message.created_at) }}</p>
            </div>
            <p class="text-sm text-gray-600 truncate">
              <span v-if="conversation.last_message.is_from_me" class="text-gray-500">You: </span>
              {{ conversation.last_message.content }}
            </p>
          </div>

          <!-- Unread Badge -->
          <div v-if="conversation.unread_count > 0" class="ml-3">
            <span class="bg-red-500 text-white text-xs rounded-full px-2 py-1 animate-pulse">
              {{ conversation.unread_count }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Chat Modal -->
    <div v-if="selectedChat" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg w-full max-w-2xl h-[80vh] flex flex-col animate-scale-in">
        <!-- Chat Header -->
        <div class="flex items-center justify-between p-4 border-b border-gray-200">
          <div class="flex items-center">
            <div class="w-8 h-8 rounded-full overflow-hidden mr-3">
              <img 
                v-if="selectedChat.profile_picture" 
                :src="`http://localhost:5001${selectedChat.profile_picture}`" 
                :alt="selectedChat.username"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full bg-gray-300 flex items-center justify-center">
                <UserIcon class="w-4 h-4 text-gray-600" />
              </div>
            </div>
            <div>
              <h3 class="font-medium text-gray-900">{{ selectedChat.username }}</h3>
              <p class="text-sm text-gray-500">Active now</p>
            </div>
          </div>
          <button @click="closeChat" class="text-gray-400 hover:text-gray-600 transition-colors">
            <XMarkIcon class="w-5 h-5" />
          </button>
        </div>

        <!-- Messages -->
        <div class="flex-1 overflow-y-auto p-4 space-y-4">
          <div v-if="messagesLoading" class="text-center py-8">
            <div class="spinner w-8 h-8 mx-auto"></div>
          </div>

          <div v-else-if="messages.length === 0" class="text-center py-8">
            <p class="text-gray-500">No messages yet. Start the conversation!</p>
          </div>

          <div v-else class="space-y-4">
            <div 
              v-for="message in messages" 
              :key="message.id"
              class="flex"
              :class="message.is_from_me ? 'justify-end' : 'justify-start'"
            >
              <div 
                class="max-w-xs px-4 py-2 rounded-lg"
                :class="message.is_from_me 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-200 text-gray-900'"
              >
                <p class="text-sm">{{ message.content }}</p>
                <p class="text-xs mt-1 opacity-70">
                  {{ formatTimeAgo(message.created_at) }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Message Input -->
        <div class="p-4 border-t border-gray-200">
          <div class="flex items-center space-x-3">
            <input
              v-model="newMessage"
              @keyup.enter="sendMessage"
              type="text"
              placeholder="Message..."
              class="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-white text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <button
              @click="sendMessage"
              :disabled="!newMessage.trim() || sendingMessage"
              class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <div v-if="sendingMessage" class="flex items-center">
                <div class="spinner w-4 h-4 mr-2"></div>
                Sending...
              </div>
              <span v-else>Send</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, inject } from 'vue'
import { 
  ChatBubbleLeftRightIcon, 
  UserIcon, 
  PaperAirplaneIcon, 
  XMarkIcon 
} from '@heroicons/vue/24/outline'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { useSocket } from '~/composables/useSocket'

dayjs.extend(relativeTime)

// State
const conversations = ref([])
const followingUsers = ref([])
const loading = ref(true)
const selectedChat = ref(null)

// WebSocket
const { socket, isConnected, joinChatRoom, leaveChatRoom, onNewMessage } = useSocket()
const messages = ref([])
const messagesLoading = ref(false)
const newMessage = ref('')
const sendingMessage = ref(false)

// Get layout functions for real-time updates
const layout = inject('layout', null)

// Format time ago
const formatTimeAgo = (dateString) => {
  return dayjs(dateString).fromNow()
}

// Fetch conversations
const fetchConversations = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      navigateTo('/login')
      return
    }

    const response = await fetch('http://localhost:5001/api/messages/conversations', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      conversations.value = data.conversations
    } else {
      console.error('Failed to fetch conversations')
    }
  } catch (error) {
    console.error('Error fetching conversations:', error)
  } finally {
    loading.value = false
  }
}

// Fetch following users
const fetchFollowingUsers = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('http://localhost:5001/api/users/following', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      followingUsers.value = data.following
    }
  } catch (error) {
    console.error('Error fetching following users:', error)
  }
}

// Fetch messages for a conversation
const fetchMessages = async (partnerId) => {
  messagesLoading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`http://localhost:5001/api/messages/${partnerId}/messages`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      messages.value = data.messages
      
      // Mark messages as read immediately
      await markMessagesAsRead(partnerId)
    }
  } catch (error) {
    console.error('Error fetching messages:', error)
  } finally {
    messagesLoading.value = false
  }
}

// Mark messages as read (real-time)
const markMessagesAsRead = async (partnerId) => {
  try {
    const token = localStorage.getItem('token')
          await fetch(`http://localhost:5001/api/messages/conversations/${partnerId}/mark-read`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })

    // Update the conversation unread count immediately
    const conversation = conversations.value.find(c => c.partner.id === partnerId)
    if (conversation) {
      conversation.unread_count = 0
    }
    
    // Update the sidebar count immediately
    if (layout && layout.fetchUnreadCounts) {
      layout.fetchUnreadCounts()
    }
  } catch (error) {
    console.error('Error marking messages as read:', error)
  }
}

// Send message
const sendMessage = async () => {
  if (!newMessage.value.trim() || !selectedChat.value) return

  sendingMessage.value = true
  const messageContent = newMessage.value.trim()
  
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`http://localhost:5001/api/messages/${selectedChat.value.id}/send`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ content: messageContent })
    })

    if (response.ok) {
      // Clear input only after successful send
      newMessage.value = ''
      console.log('Message sent successfully, waiting for WebSocket event')
    } else {
      console.error('Failed to send message')
      // Keep the message in the input if it failed
    }
  } catch (error) {
    console.error('Error sending message:', error)
    // Keep the message in the input if there was an error
  } finally {
    sendingMessage.value = false
  }
}

// Open chat
const openChat = async (user) => {
  selectedChat.value = user
  await fetchMessages(user.id)
  
  // Join chat room for real-time messages
  console.log('Opening chat with user:', user.id)
  joinChatRoom(user.id)
}

// Close chat
const closeChat = () => {
  if (selectedChat.value) {
    // Leave chat room
    leaveChatRoom(selectedChat.value.id)
  }
  selectedChat.value = null
  messages.value = []
}

// Set up real-time message listener
const setupRealtimeMessages = () => {
  onNewMessage((messageData) => {
    console.log('New message received:', messageData)
    
    // Get current user
    const currentUser = JSON.parse(localStorage.getItem('user'))
    if (!currentUser) return
    
    // Determine if this message is from the current user
    const isFromMe = messageData.sender_id === currentUser.id
    
    // Create the message object with is_from_me flag
    const messageWithFlag = {
      ...messageData,
      is_from_me: isFromMe,
      partner_id: isFromMe ? messageData.receiver_id : messageData.sender_id
    }
    
    // Add message to current chat if we have a selected chat and the message belongs to this conversation
    if (selectedChat.value && messageWithFlag.partner_id === selectedChat.value.id) {
      messages.value.push(messageWithFlag)
    }
    
    // Update conversation list
    // Find the conversation with the partner_id
    const conversation = conversations.value.find(c => c.partner.id === messageWithFlag.partner_id)
    
    if (conversation) {
      conversation.last_message = {
        content: messageWithFlag.content,
        created_at: messageWithFlag.created_at,
        is_from_me: messageWithFlag.is_from_me
      }
      
      // Only increment unread count if the message is not from us
      if (!messageWithFlag.is_from_me) {
        conversation.unread_count++
      }
    }
  })
}

// Initialize
onMounted(() => {
  fetchConversations()
  fetchFollowingUsers()
  setupRealtimeMessages()
})

onUnmounted(() => {
  if (selectedChat.value) {
    leaveChatRoom(selectedChat.value.id)
  }
})
</script>

<style scoped>
/* Animations */
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
}

.animate-scale-in {
  animation: scaleIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes scaleIn {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* Spinner */
.spinner {
  @apply animate-spin rounded-full border-2 border-gray-300 border-t-blue-600;
}
</style> 