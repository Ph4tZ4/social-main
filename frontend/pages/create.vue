<template>
  <div class="max-w-2xl mx-auto py-8 px-4">
    <div class="bg-white rounded-lg shadow-sm border border-gray-200">
      <!-- Header -->
      <div class="flex items-center justify-between p-4 border-b border-gray-200">
        <h1 class="text-xl font-semibold text-gray-900">Create New Post</h1>
      </div>

      <!-- Content -->
      <div class="p-6">
        <!-- Image Upload Area -->
        <div class="mb-6">
          <div 
            v-if="images.length === 0"
            @click="triggerFileInput"
            class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-gray-400 transition-colors"
          >
            <PhotoIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p class="text-lg font-medium text-gray-900 mb-2">Select photos</p>
            <p class="text-gray-500">Choose up to 10 photos to share</p>
          </div>

          <!-- Image Preview -->
          <div v-else class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div 
                v-for="(image, index) in images" 
                :key="index"
                class="relative aspect-square rounded-lg overflow-hidden"
              >
                <img 
                  :src="image" 
                  :alt="`Image ${index + 1}`"
                  class="w-full h-full object-cover"
                />
                <button
                  @click="removeImage(index)"
                  class="absolute top-2 right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600"
                >
                  <XMarkIcon class="w-4 h-4" />
                </button>
                <div class="absolute bottom-2 left-2 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
                  {{ index + 1 }}/{{ images.length }}
                </div>
              </div>
            </div>
            
            <button
              v-if="images.length < 10"
              @click="triggerFileInput"
              class="w-full border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-gray-400 transition-colors"
            >
              <PlusIcon class="w-6 h-6 text-gray-400 mx-auto mb-2" />
              <p class="text-gray-600">Add more photos</p>
            </button>
          </div>

          <!-- Hidden file input -->
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            multiple
            class="hidden"
            @change="handleFileSelect"
          />
        </div>

        <!-- Caption -->
        <div class="mb-6">
          <label for="caption" class="block text-sm font-medium text-gray-700 mb-2">
            Caption
          </label>
          <textarea
            id="caption"
            v-model="caption"
            rows="4"
            maxlength="2200"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            placeholder="Write a caption..."
          ></textarea>
          <div class="flex justify-between items-center mt-1">
            <p class="text-sm text-gray-500">
              {{ caption.length }}/2200
            </p>
          </div>
        </div>

        <!-- Location (Optional) -->
        <div class="mb-6">
          <label for="location" class="block text-sm font-medium text-gray-700 mb-2">
            Location (optional)
          </label>
          <input
            id="location"
            v-model="location"
            type="text"
            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Add location"
          />
        </div>

        <!-- Error Message -->
        <div v-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p class="text-sm text-red-600">{{ error }}</p>
        </div>

        <!-- Share Button -->
        <div class="flex justify-end pt-4 border-t border-gray-200">
          <button
            @click="createPost"
            :disabled="loading || images.length === 0"
            class="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div v-if="loading" class="flex items-center">
              <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Creating...
            </div>
            <span v-else>Share</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { PhotoIcon, PlusIcon, XMarkIcon } from '@heroicons/vue/24/outline'

// State
const images = ref([])
const caption = ref('')
const location = ref('')
const loading = ref(false)
const error = ref('')
const fileInput = ref(null)

// File handling
const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  
  // Validate number of files
  if (images.value.length + files.length > 10) {
    error.value = 'Maximum 10 images allowed'
    return
  }
  
  // Validate each file
  for (const file of files) {
    if (!file.type.startsWith('image/')) {
      error.value = 'Please select valid image files'
      return
    }
    
    if (file.size > 5 * 1024 * 1024) {
      error.value = 'Each image must be less than 5MB'
      return
    }
  }
  
  // Convert files to base64
  files.forEach(file => {
    const reader = new FileReader()
    reader.onload = (e) => {
      images.value.push(e.target.result)
    }
    reader.readAsDataURL(file)
  })
  
  error.value = ''
}

const removeImage = (index) => {
  images.value.splice(index, 1)
}

// Create post
const createPost = async () => {
  if (images.value.length === 0) {
    error.value = 'Please select at least one image'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      await navigateTo('/login')
      return
    }
    
    const response = await fetch('http://localhost:5001/api/posts/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        images: images.value,
        caption: caption.value.trim(),
        location: location.value.trim()
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      // Redirect to home page
      await navigateTo('/')
    } else {
      error.value = data.error || 'Failed to create post'
    }
  } catch (err) {
    error.value = 'Network error. Please try again.'
    console.error('Create post error:', err)
  } finally {
    loading.value = false
  }
}

// Check if user is logged in
onMounted(() => {
  const token = localStorage.getItem('token')
  if (!token) {
    navigateTo('/login')
  }
})
</script> 