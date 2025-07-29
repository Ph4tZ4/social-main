<template>
  <div class="space-y-6">
    <div class="bg-white rounded-lg shadow-lg border border-gray-200 animate-fade-in">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200">
        <h1 class="text-xl font-semibold text-gray-900">Notifications</h1>
      </div>

      <!-- Notifications List -->
      <div v-if="loading" class="text-center py-12">
        <div class="spinner w-12 h-12 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading notifications...</p>
      </div>

      <div v-else-if="notifications.length === 0" class="text-center py-12">
        <div class="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <BellIcon class="w-12 h-12 text-gray-400" />
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">All caught up!</h3>
        <p class="text-gray-600">You're up to date with all your notifications</p>
      </div>

      <div v-else class="divide-y divide-gray-200">
        <div 
          v-for="notification in notifications" 
          :key="notification.id"
          class="flex items-start p-4 hover:bg-gray-50 transition-colors cursor-pointer"
          :class="{ 'bg-blue-50': !notification.is_read }"
          @click="markAsRead(notification.id)"
        >
          <!-- Profile Picture -->
          <div class="w-10 h-10 rounded-full overflow-hidden mr-3">
            <img 
              v-if="notification.sender.profile_picture" 
              :src="`http://localhost:5001${notification.sender.profile_picture}`" 
              :alt="notification.sender.username"
              class="w-full h-full object-cover"
            />
            <div v-else class="w-full h-full bg-gray-300 flex items-center justify-center">
              <UserIcon class="w-5 h-5 text-gray-600" />
            </div>
          </div>

          <!-- Notification Content -->
          <div class="flex-1 min-w-0">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <p class="text-sm text-gray-900">
                  <span class="font-medium">{{ notification.sender.username }}</span>
                  {{ getNotificationText(notification.type) }}
                  <span v-if="notification.post" class="text-gray-500">your post</span>
                </p>
                <p class="text-xs text-gray-500 mt-1">{{ formatTimeAgo(notification.created_at) }}</p>
              </div>
              
              <!-- Post Thumbnail -->
              <div v-if="notification.post && notification.post.images.length > 0" class="ml-3">
                <img 
                  :src="`http://localhost:5001${notification.post.images[0]}`" 
                  :alt="notification.post.caption"
                  class="w-12 h-12 object-cover rounded"
                />
              </div>
            </div>
          </div>

          <!-- Unread Indicator -->
          <div v-if="!notification.is_read" class="ml-3">
            <div class="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
          </div>
        </div>
      </div>

      <!-- Load More -->
      <div v-if="notifications.length > 0 && hasMore" class="p-4 border-t border-gray-200">
        <button
          @click="loadMore"
          :disabled="loadingMore"
          class="w-full py-2 text-blue-600 hover:text-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <div v-if="loadingMore" class="flex items-center justify-center">
            <div class="spinner w-4 h-4 mr-2"></div>
            Loading...
          </div>
          <span v-else>Load more</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import { BellIcon, UserIcon } from '@heroicons/vue/24/outline'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

// State
const notifications = ref([])
const loading = ref(true)
const loadingMore = ref(false)
const hasMore = ref(true)
const currentPage = ref(1)

// Get layout functions for real-time updates
const layout = inject('layout', null)

// Format time ago
const formatTimeAgo = (dateString) => {
  return dayjs(dateString).fromNow()
}

// Get notification text
const getNotificationText = (type) => {
  switch (type) {
    case 'like':
      return 'liked'
    case 'comment':
      return 'commented on'
    case 'follow':
      return 'started following you'
    case 'message':
      return 'sent you a message'
    default:
      return 'interacted with'
  }
}

// Fetch notifications
const fetchNotifications = async (page = 1) => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      navigateTo('/login')
      return
    }

    const response = await fetch(`http://localhost:5001/api/notifications/?page=${page}&per_page=20`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      if (page === 1) {
        notifications.value = data.notifications
      } else {
        notifications.value.push(...data.notifications)
      }
      hasMore.value = data.notifications.length === 20
      currentPage.value = page
    } else {
      console.error('Failed to fetch notifications')
    }
  } catch (error) {
    console.error('Error fetching notifications:', error)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

// Load more notifications
const loadMore = async () => {
  if (loadingMore.value || !hasMore.value) return
  
  loadingMore.value = true
  await fetchNotifications(currentPage.value + 1)
}

// Mark single notification as read (real-time)
const markAsRead = async (notificationId) => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`http://localhost:5001/api/notifications/${notificationId}/mark-read`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      // Immediately update the notification
      const notification = notifications.value.find(n => n.id === notificationId)
      if (notification) {
        notification.is_read = true
      }
      
      // Update the sidebar count immediately
      if (layout && layout.markNotificationsAsRead) {
        layout.markNotificationsAsRead()
      }
    }
  } catch (error) {
    console.error('Error marking notification as read:', error)
  }
}

// Mark all as read (real-time) - called automatically when page loads
const markAllAsRead = async () => {
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('http://localhost:5001/api/notifications/mark-read', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ notification_ids: [] })
    })

    if (response.ok) {
      // Update all notifications to read immediately
      notifications.value.forEach(notification => {
        notification.is_read = true
      })
      
      // Update the sidebar count immediately
      if (layout && layout.markNotificationsAsRead) {
        layout.markNotificationsAsRead()
      }
    }
  } catch (error) {
    console.error('Error marking notifications as read:', error)
  }
}

// Initialize
onMounted(async () => {
  await fetchNotifications()
  // Automatically mark all notifications as read when page loads
  await markAllAsRead()
})
</script>

<style scoped>
/* Animations */
.animate-fade-in {
  animation: fadeIn 0.5s ease-out;
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

/* Spinner */
.spinner {
  @apply animate-spin rounded-full border-2 border-gray-300 border-t-blue-600;
}
</style> 