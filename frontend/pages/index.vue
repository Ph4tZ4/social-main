<template>
    <div class="space-y-6">
      <!-- Posts Feed -->
      <div v-if="loading" class="text-center py-16">
        <div class="spinner w-16 h-16 mx-auto"></div>
        <p class="mt-6 text-lg text-gray-600">Loading posts...</p>
      </div>
  
      <div v-else-if="posts.length === 0" class="text-center py-16">
        <div class="w-32 h-32 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <PhotoIcon class="w-16 h-16 text-gray-400" />
        </div>
        <h3 class="text-xl font-medium text-gray-900 mb-3">No posts yet</h3>
        <p class="text-gray-600 text-lg">Follow some users to see their posts here</p>
      </div>
  
      <div v-else class="space-y-6">
        <div v-for="post in posts" :key="post.id" class="card post-card max-w-2xl mx-auto animate-fade-in">
          <!-- Post Header -->
          <div class="flex items-center p-4 border-b border-gray-200">
            <div class="w-10 h-10 rounded-full overflow-hidden mr-3">
                              <img 
                    v-if="post.author?.profile_picture" 
                    :src="`http://localhost:5001${post.author.profile_picture}`" 
                    :alt="post.author?.username || 'User'"
                    class="w-full h-full object-cover"
                  />
              <div v-else class="w-full h-full bg-gray-300 flex items-center justify-center">
                <UserIcon class="w-5 h-5 text-gray-600" />
              </div>
            </div>
            <div class="flex-1">
              <p class="font-semibold text-gray-900">{{ post.author?.username || 'Unknown User' }}</p>
              <p class="text-sm text-gray-500">{{ formatTimeAgo(post.created_at) }}</p>
            </div>
            <button class="text-gray-400 hover:text-gray-600 p-2 transition-colors">
              <EllipsisHorizontalIcon class="w-5 h-5" />
            </button>
          </div>
  
          <!-- Post Images -->
          <div class="relative">
            <div v-if="post.images.length === 1" class="aspect-square">
                            <img 
                  :src="`http://localhost:5001${post.images[0]}`" 
                  :alt="post.caption"
                  class="w-full h-full object-cover"
                />
            </div>
            <div v-else class="relative overflow-hidden" style="max-height: 600px;">
              <div 
                class="flex transition-transform duration-300 ease-in-out"
                :style="{ transform: `translateX(-${(currentImageIndex[post.id] || 0) * 100}%)` }"
              >
                <div 
                  v-for="(image, index) in post.images" 
                  :key="index"
                  class="w-full flex-shrink-0"
                  style="min-width: 100%;"
                >
                  <img 
                    :src="`http://localhost:5001${image}`" 
                    :alt="post.caption"
                    class="w-full h-auto max-h-[600px] object-cover"
                    :style="{ aspectRatio: getFirstImageAspectRatio(post.id, post.images) }"
                  />
                </div>
              </div>
              <!-- Image Navigation -->
              <div v-if="post.images.length > 1" class="absolute inset-0 flex items-center justify-between p-2">
                <button 
                  v-if="(currentImageIndex[post.id] || 0) > 0"
                  @click="previousImage(post.id)"
                  class="nav-button w-8 h-8 bg-black bg-opacity-50 text-white rounded-full flex items-center justify-center hover:bg-opacity-70"
                >
                  <ChevronLeftIcon class="w-5 h-5" />
                </button>
                <button 
                  v-if="(currentImageIndex[post.id] || 0) < post.images.length - 1"
                  @click="nextImage(post.id)"
                  class="nav-button w-8 h-8 bg-black bg-opacity-50 text-white rounded-full flex items-center justify-center hover:bg-opacity-70 ml-auto"
                >
                  <ChevronRightIcon class="w-5 h-5" />
                </button>
              </div>
              <!-- Image Indicators -->
              <div v-if="post.images.length > 1" class="absolute bottom-2 left-1/2 transform -translate-x-1/2 flex space-x-1">
                <div 
                  v-for="(image, index) in post.images" 
                  :key="index"
                  class="w-2 h-2 rounded-full transition-all"
                  :class="(currentImageIndex[post.id] || 0) === index ? 'bg-white' : 'bg-white bg-opacity-50'"
                ></div>
              </div>
            </div>
          </div>
  
          <!-- Post Actions -->
          <div class="p-4">
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center space-x-4">
                <button 
                  @click="toggleLike(post.id)"
                  class="text-gray-600 hover:text-red-500 transition-colors p-2"
                  :class="{ 'text-red-500': post.is_liked }"
                >
                  <HeartIcon v-if="post.is_liked" class="w-6 h-6 fill-current" />
                  <HeartIcon v-else class="w-6 h-6" />
                </button>
                <button 
                  @click="openPostDetail(post)"
                  class="text-gray-600 hover:text-gray-800 transition-colors p-2"
                >
                  <ChatBubbleOvalLeftIcon class="w-6 h-6" />
                </button>
                <button class="text-gray-600 hover:text-gray-800 transition-colors p-2">
                  <PaperAirplaneIcon class="w-6 h-6" />
                </button>
              </div>
              <button class="text-gray-600 hover:text-gray-800 transition-colors p-2">
                <BookmarkIcon class="w-6 h-6" />
              </button>
            </div>
  
            <!-- Likes Count -->
            <p v-if="post.likes_count > 0" class="font-semibold text-gray-900 mb-2">
              {{ post.likes_count }} like{{ post.likes_count !== 1 ? 's' : '' }}
            </p>
  
            <!-- Caption -->
            <div v-if="post.caption" class="mb-2">
              <p class="text-gray-900">
                <span class="font-semibold">{{ post.author?.username || 'Unknown User' }}</span>
                {{ post.caption }}
              </p>
            </div>
  
            <!-- Comments Preview -->
            <div v-if="post.comments.length > 0" class="mb-2">
              <div v-for="comment in post.comments.slice(0, 2)" :key="comment.id" class="text-gray-900">
                <span class="font-semibold">{{ comment.author?.username || 'Unknown User' }}</span>
                {{ comment.content }}
              </div>
            </div>
  
            <!-- View All Comments -->
            <button 
              v-if="post.comments_count > 2"
              @click="openPostDetail(post)"
              class="text-gray-500 text-sm hover:text-gray-700 mb-3"
            >
              View all {{ post.comments_count }} comments
            </button>
  
            <!-- Add Comment -->
            <div class="flex items-center pt-3 border-t border-gray-200">
              <input
                v-model="commentText[post.id]"
                @keyup.enter="addComment(post.id)"
                type="text"
                placeholder="Add a comment..."
                class="flex-1 border-none outline-none text-sm bg-transparent text-gray-900 placeholder-gray-500"
              />
              <button 
                @click="addComment(post.id)"
                :disabled="!commentText[post.id]?.trim()"
                class="text-blue-600 font-semibold text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Post
              </button>
            </div>
          </div>
        </div>
      </div>
  
      <!-- Post Detail Modal -->
      <div v-if="selectedPost" class="fixed inset-0 backdrop-blur-md bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-xl max-w-6xl w-full max-h-[95vh] overflow-hidden shadow-2xl animate-scale-in">
          <div class="flex">
            <!-- Left Side - Images -->
            <div class="w-1/2 bg-black flex items-center justify-center">
              <div class="relative overflow-hidden w-full h-full flex items-center justify-center">
                <div 
                  class="flex transition-transform duration-300 ease-in-out"
                  :style="{ transform: `translateX(-${currentDetailImageIndex * 100}%)` }"
                >
                  <div 
                    v-for="(image, index) in selectedPost.images" 
                    :key="index"
                    class="w-full flex-shrink-0 flex items-center justify-center"
                    style="min-width: 100%;"
                  >
                                    <img 
                    :src="`http://localhost:5001${image}`" 
                    :alt="selectedPost.caption"
                    class="max-w-full max-h-full object-cover"
                    :style="{ aspectRatio: getFirstImageAspectRatio(selectedPost.id, selectedPost.images) }"
                  />
                  </div>
                </div>
                <!-- Image Navigation -->
                <div v-if="selectedPost.images.length > 1" class="absolute inset-0 flex items-center justify-between p-4">
                  <button 
                    v-if="currentDetailImageIndex > 0"
                    @click="currentDetailImageIndex--"
                    class="nav-button w-12 h-12 bg-black bg-opacity-50 text-white rounded-full flex items-center justify-center hover:bg-opacity-70"
                  >
                    <ChevronLeftIcon class="w-6 h-6" />
                  </button>
                  <button 
                    v-if="currentDetailImageIndex < selectedPost.images.length - 1"
                    @click="currentDetailImageIndex++"
                    class="w-12 h-12 bg-black bg-opacity-50 text-white rounded-full flex items-center justify-center hover:bg-opacity-70 ml-auto nav-button"
                  >
                    <ChevronRightIcon class="w-6 h-6" />
                  </button>
                </div>
              </div>
            </div>
  
            <!-- Right Side - Comments -->
            <div class="w-1/2 flex flex-col">
              <!-- Post Header -->
              <div class="flex items-center p-4 border-b border-gray-200">
                <div class="w-10 h-10 rounded-full overflow-hidden mr-3">
                  <img 
                    v-if="selectedPost.author?.profile_picture" 
                    :src="`http://localhost:5001${selectedPost.author.profile_picture}`" 
                    :alt="selectedPost.author?.username || 'User'"
                    class="w-full h-full object-cover"
                  />
                  <div v-else class="w-full h-full bg-gray-300 flex items-center justify-center">
                    <UserIcon class="w-5 h-5 text-gray-600" />
                  </div>
                </div>
                <div class="flex-1">
                  <p class="font-semibold text-gray-900">{{ selectedPost.author?.username || 'Unknown User' }}</p>
                </div>
                <button @click="selectedPost = null" class="text-gray-400 hover:text-gray-600">
                  <XMarkIcon class="w-6 h-6" />
                </button>
              </div>
  
              <!-- Comments Section -->
              <div class="flex-1 overflow-y-auto p-4">
                <!-- Caption -->
                <div v-if="selectedPost.caption" class="mb-4">
                  <p class="text-gray-900">
                    <span class="font-semibold">{{ selectedPost.author?.username || 'Unknown User' }}</span>
                    {{ selectedPost.caption }}
                  </p>
                </div>
  
                <!-- Comments -->
                <div v-if="selectedPost.comments.length > 0" class="space-y-4">
                  <div v-for="comment in selectedPost.comments" :key="comment.id" class="flex">
                    <div class="w-8 h-8 rounded-full overflow-hidden mr-3 flex-shrink-0">
                      <img 
                        v-if="comment.author?.profile_picture" 
                        :src="`http://localhost:5001${comment.author.profile_picture}`" 
                        :alt="comment.author?.username || 'User'"
                        class="w-full h-full object-cover"
                      />
                      <div v-else class="w-full h-full bg-gray-300 flex items-center justify-center">
                        <UserIcon class="w-4 h-4 text-gray-600" />
                      </div>
                    </div>
                    <div class="flex-1">
                      <p class="text-gray-900">
                        <span class="font-semibold">{{ comment.author?.username || 'Unknown User' }}</span>
                        {{ comment.content }}
                      </p>
                      <p class="text-sm text-gray-500 mt-1">{{ formatTimeAgo(comment.created_at) }}</p>
                    </div>
                  </div>
                </div>
              </div>
  
              <!-- Add Comment -->
              <div class="p-4 border-t border-gray-200">
                <div class="flex items-center">
                  <input
                    v-model="detailCommentText"
                    @keyup.enter="addDetailComment"
                    type="text"
                    placeholder="Add a comment..."
                    class="flex-1 border-none outline-none text-sm bg-transparent text-gray-900 placeholder-gray-500"
                  />
                  <button 
                    @click="addDetailComment"
                    :disabled="!detailCommentText?.trim()"
                    class="text-blue-600 font-semibold text-sm disabled:opacity-50 disabled:cursor-not-allowed ml-4"
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
  import { ref, onMounted, onUnmounted } from 'vue'
  import { 
    PhotoIcon,
    UserIcon, 
    HeartIcon, 
    ChatBubbleOvalLeftIcon, 
    PaperAirplaneIcon, 
    BookmarkIcon, 
    EllipsisHorizontalIcon,
    ChevronLeftIcon,
    ChevronRightIcon,
    XMarkIcon
  } from '@heroicons/vue/24/outline'
  import dayjs from 'dayjs'
  import relativeTime from 'dayjs/plugin/relativeTime'
  import { useSocket } from '~/composables/useSocket'
  
  dayjs.extend(relativeTime)
  
  const loading = ref(true)
  const posts = ref([])
  const selectedPost = ref(null)
  const currentDetailImageIndex = ref(0)
  const currentImageIndex = ref({})
  const commentText = ref({})
  const detailCommentText = ref('')
  const imageAspectRatios = ref({})
  
  // WebSocket
  const { onNewComment, onNewLike } = useSocket()
  
  // Set up real-time listeners
  const setupRealtimeListeners = () => {
    // Listen for new comments
    onNewComment((data) => {
      console.log('New comment received:', data)
      const post = posts.value.find(p => p.id === data.post_id)
      if (post) {
        post.comments.unshift(data.comment)
        post.comments_count++
      }
      
      // Update selected post if it's the same post
      if (selectedPost.value && selectedPost.value.id === data.post_id) {
        selectedPost.value.comments.unshift(data.comment)
        selectedPost.value.comments_count++
      }
    })
  
    // Listen for new likes
    onNewLike((data) => {
      console.log('New like received:', data)
      const post = posts.value.find(p => p.id === data.post_id)
      if (post) {
        post.likes_count++
      }
      
      // Update selected post if it's the same post
      if (selectedPost.value && selectedPost.value.id === data.post_id) {
        selectedPost.value.likes_count++
      }
    })
  }
  
  onMounted(() => {
    fetchPosts()
    setupRealtimeListeners()
  })
  
  onUnmounted(() => {
    // Clean up listeners if needed
  })
  
  const fetchPosts = async () => {
    try {
      const token = localStorage.getItem('token')
      if (!token) {
        navigateTo('/login')
        return
      }
  
      const response = await fetch('http://localhost:5001/api/posts/feed', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
  
      if (response.ok) {
        const data = await response.json()
        posts.value = data.posts
      } else {
        console.error('Failed to fetch posts')
      }
    } catch (error) {
      console.error('Error fetching posts:', error)
    } finally {
      loading.value = false
    }
  }
  
  const formatTimeAgo = (date) => {
    return dayjs(date).fromNow()
  }
  
  const toggleLike = async (postId) => {
    try {
      const token = localStorage.getItem('token')
      const post = posts.value.find(p => p.id === postId)
      
      if (!post) return
  
      const response = await fetch(`http://localhost:5001/api/posts/${postId}/like`, {
        method: post.is_liked ? 'DELETE' : 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
  
      if (response.ok) {
        post.is_liked = !post.is_liked
        post.likes_count += post.is_liked ? 1 : -1
      }
    } catch (error) {
      console.error('Error toggling like:', error)
    }
  }
  
  const addComment = async (postId) => {
    try {
      const token = localStorage.getItem('token')
      const text = commentText.value[postId]?.trim()
      
      if (!text) return
  
      const response = await fetch(`http://localhost:5001/api/posts/${postId}/comments`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: text })
      })
  
      if (response.ok) {
        const responseData = await response.json()
        const newComment = responseData.comment
        const post = posts.value.find(p => p.id === postId)
        if (post) {
          post.comments.unshift(newComment)
          post.comments_count += 1
          commentText.value[postId] = ''
        }
      }
    } catch (error) {
      console.error('Error adding comment:', error)
    }
  }
  
  const addDetailComment = async () => {
    if (!selectedPost.value) return
    
    try {
      const token = localStorage.getItem('token')
      const text = detailCommentText.value?.trim()
      
      if (!text) return
  
      const response = await fetch(`http://localhost:5001/api/posts/${selectedPost.value.id}/comments`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ content: text })
      })
  
      if (response.ok) {
        const responseData = await response.json()
        const newComment = responseData.comment
        selectedPost.value.comments.unshift(newComment)
        selectedPost.value.comments_count += 1
        detailCommentText.value = ''
      }
    } catch (error) {
      console.error('Error adding detail comment:', error)
    }
  }
  
  const openPostDetail = (post) => {
    selectedPost.value = { ...post }
    currentDetailImageIndex.value = 0
  }
  
  const nextImage = (postId) => {
    const post = posts.value.find(p => p.id === postId)
    if (post && (currentImageIndex.value[postId] || 0) < post.images.length - 1) {
      currentImageIndex.value = {
        ...currentImageIndex.value,
        [postId]: (currentImageIndex.value[postId] || 0) + 1
      }
    }
  }
  
  const previousImage = (postId) => {
    if ((currentImageIndex.value[postId] || 0) > 0) {
      currentImageIndex.value = {
        ...currentImageIndex.value,
        [postId]: (currentImageIndex.value[postId] || 0) - 1
      }
    }
  }
  
  const getFirstImageAspectRatio = (postId, images) => {
    if (!images || images.length === 0) return '1'
    
    // Return cached aspect ratio if available
    if (imageAspectRatios.value[postId]) {
      return imageAspectRatios.value[postId]
    }
    
    // Calculate aspect ratio for first image
    const img = new Image()
    img.onload = () => {
      const aspectRatio = img.width / img.height
      imageAspectRatios.value[postId] = aspectRatio.toString()
    }
    img.onerror = () => {
      imageAspectRatios.value[postId] = '1' // Default to square if image fails to load
    }
        img.src = `http://localhost:5001${images[0]}`
    
    // Return default while loading
    return imageAspectRatios.value[postId] || '1'
  }
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
  
  /* Post card styles */
  .post-card {
    @apply bg-white rounded-lg shadow-lg border border-gray-200 overflow-hidden transition-all duration-200;
  }
  
  .post-card:hover {
    @apply shadow-xl transform scale-[1.02];
  }
  
  /* Image sliding animations */
  .image-slider {
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }
  
  .image-slider:hover {
    transform: scale(1.02);
  }
  
  /* Smooth image transitions */
  .image-container {
    transition: all 0.3s ease-in-out;
  }
  
  /* Enhanced button hover effects */
  .nav-button {
    transition: all 0.2s ease-in-out;
  }
  
  .nav-button:hover {
    transform: scale(1.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  }
  </style> 