<template>
  <div class="max-w-2xl mx-auto py-8 px-4">
    <!-- Search Header -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900 mb-4">Search</h1>
      
      <!-- Search Input -->
      <div class="relative">
        <MagnifyingGlassIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          v-model="searchQuery"
          @input="handleSearch"
          type="text"
          placeholder="Search users..."
          class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">Searching...</p>
    </div>

    <!-- No Results -->
    <div v-else-if="searchQuery && users.length === 0" class="text-center py-12">
      <div class="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <UserIcon class="w-12 h-12 text-gray-400" />
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">No users found</h3>
      <p class="text-gray-600">Try searching with a different username</p>
    </div>

    <!-- Search Results -->
    <div v-else-if="searchQuery && users.length > 0" class="space-y-4">
      <div v-for="user in users" :key="user.id" class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <!-- Profile Picture -->
            <div class="w-12 h-12 rounded-full overflow-hidden">
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

            <!-- User Info -->
            <div class="flex-1">
              <h3 class="font-medium text-gray-900">{{ user.username }}</h3>
              <p v-if="user.bio" class="text-sm text-gray-600 mt-1">{{ user.bio }}</p>
              <div class="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                <span>{{ user.followers_count }} follower{{ user.followers_count !== 1 ? 's' : '' }}</span>
                <span>{{ user.following_count }} following</span>
              </div>
            </div>
          </div>

          <!-- Follow Button -->
          <button
            @click="toggleFollow(user.id)"
            :disabled="followLoading[user.id]"
            class="px-4 py-2 rounded-lg font-medium text-sm transition-colors"
            :class="user.is_following 
              ? 'bg-gray-200 text-gray-700 hover:bg-gray-300' 
              : 'bg-blue-600 text-white hover:bg-blue-700'"
          >
            <div v-if="followLoading[user.id]" class="flex items-center">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
              Loading...
            </div>
            <span v-else>{{ user.is_following ? 'Following' : 'Follow' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Suggestions (when no search query) -->
    <div v-else class="space-y-6">
      <h2 class="text-xl font-semibold text-gray-900">Suggested for you</h2>
      
      <div v-if="suggestionsLoading" class="text-center py-12">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p class="mt-4 text-gray-600">Loading suggestions...</p>
      </div>

      <div v-else-if="suggestions.length === 0" class="text-center py-12">
        <div class="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <UserIcon class="w-12 h-12 text-gray-400" />
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">No suggestions</h3>
        <p class="text-gray-600">Start following users to get suggestions</p>
      </div>

      <div v-else class="space-y-4">
        <div v-for="user in suggestions" :key="user.id" class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
              <!-- Profile Picture -->
              <div class="w-12 h-12 rounded-full overflow-hidden">
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

              <!-- User Info -->
              <div class="flex-1">
                <h3 class="font-medium text-gray-900">{{ user.username }}</h3>
                <p v-if="user.bio" class="text-sm text-gray-600 mt-1">{{ user.bio }}</p>
                <div class="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                  <span>{{ user.followers_count }} follower{{ user.followers_count !== 1 ? 's' : '' }}</span>
                </div>
              </div>
            </div>

            <!-- Follow Button -->
            <button
              @click="toggleFollow(user.id)"
              :disabled="followLoading[user.id]"
              class="px-4 py-2 rounded-lg font-medium text-sm transition-colors bg-blue-600 text-white hover:bg-blue-700"
            >
              <div v-if="followLoading[user.id]" class="flex items-center">
                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                Loading...
              </div>
              <span v-else>Follow</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { MagnifyingGlassIcon, UserIcon } from '@heroicons/vue/24/outline'

// State
const searchQuery = ref('')
const users = ref([])
const suggestions = ref([])
const loading = ref(false)
const suggestionsLoading = ref(false)
const followLoading = reactive({})

// Debounce search
let searchTimeout = null

const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    if (searchQuery.value.trim()) {
      searchUsers()
    } else {
      users.value = []
    }
  }, 300)
}

// Search users
const searchUsers = async () => {
  if (!searchQuery.value.trim()) return

  loading.value = true
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      await navigateTo('/login')
      return
    }

    const response = await fetch(`http://localhost:5001/api/users/search?q=${encodeURIComponent(searchQuery.value.trim())}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      users.value = data.users
    } else {
      console.error('Failed to search users')
    }
  } catch (error) {
    console.error('Error searching users:', error)
  } finally {
    loading.value = false
  }
}

// Fetch suggestions
const fetchSuggestions = async () => {
  suggestionsLoading.value = true
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      await navigateTo('/login')
      return
    }

    const response = await fetch('http://localhost:5001/api/users/suggestions', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      suggestions.value = data.suggestions
    } else {
      console.error('Failed to fetch suggestions')
    }
  } catch (error) {
    console.error('Error fetching suggestions:', error)
  } finally {
    suggestionsLoading.value = false
  }
}

// Toggle follow
const toggleFollow = async (userId) => {
  followLoading[userId] = true
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`http://localhost:5001/api/users/${userId}/follow`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      
      // Update user in search results
      const user = users.value.find(u => u.id === userId)
      if (user) {
        user.is_following = data.is_following
        user.followers_count += data.is_following ? 1 : -1
      }
      
      // Update user in suggestions
      const suggestion = suggestions.value.find(u => u.id === userId)
      if (suggestion) {
        suggestion.is_following = data.is_following
        suggestion.followers_count += data.is_following ? 1 : -1
      }
    }
  } catch (error) {
    console.error('Error toggling follow:', error)
  } finally {
    followLoading[userId] = false
  }
}

// Initialize
onMounted(() => {
  fetchSuggestions()
})
</script> 