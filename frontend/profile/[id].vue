<template>
  <div class="max-w-4xl mx-auto py-8 px-4">
    <!-- Profile Header -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      <div class="flex items-start space-x-8">
        <!-- Profile Picture -->
        <div class="w-32 h-32 rounded-full overflow-hidden flex-shrink-0">
          <img 
            v-if="profile.profile_picture" 
            :src="`http://localhost:5001${profile.profile_picture}`" 
            :alt="profile.username"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full bg-gray-300 flex items-center justify-center">
            <UserIcon class="w-16 h-16 text-gray-600" />
          </div>
        </div>

        <!-- Profile Info -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center space-x-4 mb-4">
            <h1 class="text-2xl font-light text-gray-900">{{ profile.username }}</h1>
            
            <!-- Follow/Unfollow Button -->
            <button 
              v-if="!profile.is_own_profile"
              @click="toggleFollow"
              :disabled="followLoading"
              class="px-6 py-2 rounded-lg font-medium transition-colors"
              :class="profile.is_following 
                ? 'bg-gray-200 text-gray-900 hover:bg-gray-300' 
                : 'bg-blue-600 text-white hover:bg-blue-700'"
            >
              <div v-if="followLoading" class="flex items-center">
                <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></div>
                Loading...
              </div>
              <span v-else>{{ profile.is_following ? 'Following' : 'Follow' }}</span>
            </button>

            <!-- Edit Profile Button -->
            <button 
              v-if="profile.is_own_profile"
              @click="editProfile"
              class="px-6 py-2 bg-gray-200 text-gray-900 rounded-lg font-medium hover:bg-gray-300 transition-colors"
            >
              Edit Profile
            </button>

            <!-- Settings Button -->
            <button class="p-2 text-gray-600 hover:text-gray-900">
              <Cog6ToothIcon class="w-5 h-5" />
            </button>
          </div>

          <!-- Stats -->
          <div class="flex space-x-8 mb-4">
            <div class="text-center">
              <span class="block font-semibold text-gray-900">{{ profile.posts_count }}</span>
              <span class="text-sm text-gray-600">posts</span>
            </div>
            <div class="text-center">
              <span class="block font-semibold text-gray-900">{{ profile.followers_count }}</span>
              <span class="text-sm text-gray-600">followers</span>
            </div>
            <div class="text-center">
              <span class="block font-semibold text-gray-900">{{ profile.following_count }}</span>
              <span class="text-sm text-gray-600">following</span>
            </div>
          </div>

          <!-- Bio -->
          <div v-if="profile.bio" class="mb-4">
            <p class="text-gray-900">{{ profile.bio }}</p>
          </div>

          <!-- Joined Date -->
          <div class="text-sm text-gray-500">
            Joined {{ formatDate(profile.created_at) }}
          </div>
        </div>
      </div>
    </div>

    <!-- Posts Grid -->
    <div v-if="loading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">Loading posts...</p>
    </div>

    <div v-else-if="posts.length === 0" class="text-center py-12">
      <div class="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
        <PhotoIcon class="w-12 h-12 text-gray-400" />
      </div>
      <h3 class="text-lg font-medium text-gray-900 mb-2">
        {{ profile.is_own_profile ? 'No posts yet' : 'No posts' }}
      </h3>
      <p class="text-gray-600">
        {{ profile.is_own_profile 
          ? 'Share your first photo or video' 
          : `${profile.username} hasn\'t shared any posts yet` }}
      </p>
      <button 
        v-if="profile.is_own_profile"
        @click="navigateTo('/create')"
        class="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        Create Post
      </button>
    </div>

    <div v-else class="grid grid-cols-3 gap-1 md:gap-4">
      <div 
        v-for="post in posts" 
        :key="post.id"
        @click="openPostDetail(post)"
        class="aspect-square bg-gray-100 rounded-lg overflow-hidden cursor-pointer group relative"
      >
        <img 
          :src="`http://localhost:5001${post.images[0]}`" 
          :alt="post.caption"
          class="w-full h-full object-cover group-hover:opacity-90 transition-opacity"
        />
        
        <!-- Multiple Images Indicator -->
        <div v-if="post.images.length > 1" class="absolute top-2 right-2">
          <svg class="w-6 h-6 text-white drop-shadow" fill="currentColor" viewBox="0 0 20 20">
            <path d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z"/>
          </svg>
        </div>

        <!-- Hover Overlay -->
        <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all flex items-center justify-center">
          <div class="opacity-0 group-hover:opacity-100 transition-opacity flex items-center space-x-6 text-white">
            <div class="flex items-center space-x-2">
              <HeartIcon class="w-6 h-6" />
              <span class="font-medium">{{ post.likes_count }}</span>
            </div>
            <div class="flex items-center space-x-2">
              <ChatBubbleOvalLeftIcon class="w-6 h-6" />
              <span class="font-medium">{{ post.comments_count }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Post Detail Modal -->
    <div v-if="selectedPost" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        <div class="flex">
          <!-- Left Side - Images -->
          <div class="w-1/2 bg-black">
            <div class="relative aspect-square">
              <img 
                :src="`http://localhost:5001${selectedPost.images[currentDetailImageIndex]}`" 
                :alt="selectedPost.caption"
                class="w-full h-full object-contain"
              />
              <!-- Image Navigation -->
              <div v-if="selectedPost.images.length > 1" class="absolute inset-0 flex items-center justify-between p-2">
                <button 
                  v-if="currentDetailImageIndex > 0"
                  @click="previousDetailImage"
                  class="w-8 h-8 bg-black bg-opacity-50 text-white rounded-full flex items-center justify-center hover:bg-opacity-70"
                >
                  <ChevronLeftIcon class="w-5 h-5" />
                </button>
                <button 
                  v-if="currentDetailImageIndex < selectedPost.images.length - 1"
                  @click="nextDetailImage"
                  class="w-8 h-8 bg-black bg-opacity-50 text-white rounded-full flex items-center justify-center hover:bg-opacity-70 ml-auto"
                >
                  <ChevronRightIcon class="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>

          <!-- Right Side - Comments -->
          <div class="w-1/2 flex flex-col">
            <!-- Post Header -->
            <div class="flex items-center justify-between p-4 border-b border-gray-200">
              <div class="flex items-center">
                <div class="w-8 h-8 rounded-full overflow-hidden mr-3">
                  <img 
                    v-if="profile.profile_picture" 
                    :src="`http://localhost:5001${profile.profile_picture}`" 
                    :alt="profile.username"
                    class="w-full h-full object-cover"
                  />
                  <div v-else class="w-full h-full bg-gray-300 flex items-center justify-center">
                    <UserIcon class="w-4 h-4 text-gray-600" />
                  </div>
                </div>
                <span class="font-medium text-gray-900">{{ profile.username }}</span>
              </div>
              <button @click="closePostDetail" class="text-gray-400 hover:text-gray-600">
                <XMarkIcon class="w-5 h-5" />
              </button>
            </div>

            <!-- Comments -->
            <div class="flex-1 overflow-y-auto p-4">
              <div v-if="selectedPost.comments.length === 0" class="text-center py-8">
                <p class="text-gray-500">No comments yet. Be the first to comment!</p>
              </div>
              <div v-else class="space-y-4">
                <div v-for="comment in selectedPost.comments" :key="comment.id" class="flex">
                  <div class="w-8 h-8 rounded-full overflow-hidden mr-3 flex-shrink-0">
                    <img 
                      v-if="comment.author.profile_picture" 
                      :src="`http://localhost:5001${comment.author.profile_picture}`" 
                      :alt="comment.author.username"
                      class="w-full h-full object-cover"
                    />
                    <div v-else class="w-full h-full bg-gray-300 flex items-center justify-center">
                      <UserIcon class="w-4 h-4 text-gray-600" />
                    </div>
                  </div>
                  <div class="flex-1">
                    <p class="text-sm">
                      <span class="font-medium text-gray-900">{{ comment.author.username }}</span>
                      <span class="text-gray-900 ml-2">{{ comment.content }}</span>
                    </p>
                    <p class="text-xs text-gray-500 mt-1">{{ formatTimeAgo(comment.created_at) }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Add Comment -->
            <div class="p-4 border-t border-gray-200">
              <div class="flex items-center space-x-3">
                <input
                  v-model="commentText"
                  @keyup.enter="addComment"
                  type="text"
                  placeholder="Add a comment..."
                  class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
                <button 
                  @click="addComment"
                  :disabled="!commentText.trim()"
                  class="text-blue-600 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Post
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { 
  UserIcon, 
  PhotoIcon, 
  HeartIcon, 
  ChatBubbleOvalLeftIcon, 
  Cog6ToothIcon,
  XMarkIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

// Route params
const route = useRoute()
const userId = route.params.id

// State
const profile = ref({})
const posts = ref([])
const loading = ref(true)
const followLoading = ref(false)
const selectedPost = ref(null)
const currentDetailImageIndex = ref(0)
const commentText = ref('')

// Format time ago
const formatTimeAgo = (dateString) => {
  return dayjs(dateString).fromNow()
}

// Format date
const formatDate = (dateString) => {
  return dayjs(dateString).format('MMMM YYYY')
}

// Fetch profile
const fetchProfile = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      await navigateTo('/login')
      return
    }

    const response = await fetch(`http://localhost:5001/api/users/${userId}/profile`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (response.ok) {
      const data = await response.json()
      profile.value = data.user
      posts.value = data.posts
    } else {
      console.error('Failed to fetch profile')
    }
  } catch (error) {
    console.error('Error fetching profile:', error)
  } finally {
    loading.value = false
  }
}

// Toggle follow
const toggleFollow = async () => {
  if (followLoading.value) return
  
  followLoading.value = true
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
      profile.value.is_following = data.is_following
      profile.value.followers_count += data.is_following ? 1 : -1
    } else {
      console.error('Failed to follow/unfollow')
    }
  } catch (error) {
    console.error('Error following/unfollowing:', error)
  } finally {
    followLoading.value = false
  }
}

// Edit profile
const editProfile = () => {
  navigateTo('/edit-profile')
}

// Open post detail
const openPostDetail = (post) => {
  selectedPost.value = post
  currentDetailImageIndex.value = 0
  commentText.value = ''
}

// Close post detail
const closePostDetail = () => {
  selectedPost.value = null
  currentDetailImageIndex.value = 0
  commentText.value = ''
}

// Navigate detail images
const nextDetailImage = () => {
  if (currentDetailImageIndex.value < selectedPost.value.images.length - 1) {
    currentDetailImageIndex.value++
  }
}

const previousDetailImage = () => {
  if (currentDetailImageIndex.value > 0) {
    currentDetailImageIndex.value--
  }
}

// Add comment
const addComment = async () => {
  if (!commentText.value.trim() || !selectedPost.value) return

  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`http://localhost:5001/api/posts/${selectedPost.value.id}/comments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ content: commentText.value.trim() })
    })

    if (response.ok) {
      const data = await response.json()
      selectedPost.value.comments.push(data.comment)
      selectedPost.value.comments_count++
      commentText.value = ''
    } else {
      console.error('Failed to add comment')
    }
  } catch (error) {
    console.error('Error adding comment:', error)
  }
}

// On mount
onMounted(() => {
  fetchProfile()
})
</script> 