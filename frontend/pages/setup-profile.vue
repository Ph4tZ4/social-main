<template>
  <div class="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Title -->
      <div class="text-center">
        <h1 class="text-3xl font-bold text-gray-900 mb-2">Set up your profile</h1>
        <p class="text-gray-600">Add a profile picture and bio to complete your account</p>
      </div>

      <!-- Profile Setup Form -->
      <div class="bg-white py-8 px-6 shadow-lg rounded-lg">
        <form @submit.prevent="handleSetupProfile" class="space-y-6">
          <!-- Profile Picture Upload -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-4">
              Profile Picture
            </label>
            
            <!-- Image Preview -->
            <div class="flex justify-center mb-4">
              <div class="relative">
                <div 
                  class="w-32 h-32 rounded-full overflow-hidden border-2 border-gray-300 bg-gray-100 flex items-center justify-center cursor-pointer"
                  @click="triggerFileInput"
                >
                  <img 
                    v-if="profileImage" 
                    :src="profileImage" 
                    alt="Profile preview"
                    class="w-full h-full object-cover"
                  />
                  <div v-else class="text-gray-400">
                    <UserIcon class="w-12 h-12 mx-auto" />
                    <p class="text-sm mt-2">Click to upload</p>
                  </div>
                </div>
                
                <!-- Remove button -->
                <button
                  v-if="profileImage"
                  type="button"
                  @click="removeProfileImage"
                  class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                >
                  <XMarkIcon class="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <!-- Hidden file input -->
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              class="hidden"
              @change="handleFileSelect"
            />
            
            <p class="text-sm text-gray-500 text-center">
              Upload a profile picture (optional)
            </p>
          </div>

          <!-- Bio Field -->
          <div>
            <label for="bio" class="block text-sm font-medium text-gray-700 mb-2">
              Bio
            </label>
            <textarea
              id="bio"
              v-model="form.bio"
              rows="3"
              maxlength="150"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              :class="{ 'border-red-500': errors.bio }"
              placeholder="Tell us about yourself..."
            ></textarea>
            <div class="flex justify-between items-center mt-1">
              <p v-if="errors.bio" class="text-sm text-red-600">
                {{ errors.bio }}
              </p>
              <p class="text-sm text-gray-500">
                {{ form.bio.length }}/150
              </p>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 rounded-md p-4">
            <p class="text-sm text-red-600">{{ error }}</p>
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg
              v-if="loading"
              class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
            >
              <circle
                class="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                stroke-width="4"
              ></circle>
              <path
                class="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              ></path>
            </svg>
            {{ loading ? 'Setting up profile...' : 'Complete setup' }}
          </button>

          <!-- Skip Button -->
          <button
            type="button"
            @click="skipSetup"
            class="w-full py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Skip for now
          </button>
        </form>
      </div>
    </div>

    <!-- Image Cropper Modal -->
    <div v-if="showCropper" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Crop your profile picture</h3>
        
        <div class="mb-4">
          <img 
            :src="cropperImage" 
            alt="Crop preview"
            class="w-full h-64 object-cover rounded-lg"
            ref="cropImage"
          />
        </div>
        
        <div class="flex justify-end space-x-3">
          <button
            type="button"
            @click="cancelCrop"
            class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="button"
            @click="applyCrop"
            class="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700"
          >
            Apply
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { UserIcon, XMarkIcon } from '@heroicons/vue/24/outline'

// Form data
const form = reactive({
  bio: ''
})

// Form state
const loading = ref(false)
const error = ref('')
const errors = reactive({
  bio: ''
})

// Image handling
const fileInput = ref(null)
const profileImage = ref('')
const cropperImage = ref('')
const showCropper = ref(false)

// Validation
const validateForm = () => {
  errors.bio = ''
  
  if (form.bio.length > 150) {
    errors.bio = 'Bio must be 150 characters or less'
    return false
  }
  
  return true
}

// File handling
const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (!file) return
  
  // Validate file type
  if (!file.type.startsWith('image/')) {
    error.value = 'Please select a valid image file'
    return
  }
  
  // Validate file size (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    error.value = 'Image size must be less than 5MB'
    return
  }
  
  // Show cropper
  const reader = new FileReader()
  reader.onload = (e) => {
    cropperImage.value = e.target.result
    showCropper.value = true
  }
  reader.readAsDataURL(file)
}

const removeProfileImage = () => {
  profileImage.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const cancelCrop = () => {
  showCropper.value = false
  cropperImage.value = ''
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const applyCrop = () => {
  // For simplicity, we'll use the original image
  // In a real app, you'd implement actual cropping
  profileImage.value = cropperImage.value
  showCropper.value = false
  cropperImage.value = ''
}

// Handle profile setup
const handleSetupProfile = async () => {
  if (!validateForm()) return
  
  loading.value = true
  error.value = ''
  
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      await navigateTo('/login')
      return
    }
    
    const response = await fetch('http://localhost:5001/api/auth/setup-profile', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        profile_picture: profileImage.value,
        bio: form.bio.trim()
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      // Update stored user data
      const userData = JSON.parse(localStorage.getItem('user') || '{}')
      userData.profile_picture = data.user.profile_picture
      userData.bio = data.user.bio
      localStorage.setItem('user', JSON.stringify(userData))
      
      // Redirect to home page
      await navigateTo('/')
    } else {
      error.value = data.error || 'Failed to set up profile'
    }
  } catch (err) {
    error.value = 'Network error. Please try again.'
    console.error('Profile setup error:', err)
  } finally {
    loading.value = false
  }
}

const skipSetup = async () => {
  await navigateTo('/')
}

// Check if user is logged in
onMounted(() => {
  const token = localStorage.getItem('token')
  if (!token) {
    navigateTo('/login')
  }
})
</script> 