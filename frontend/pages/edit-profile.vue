<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-2xl mx-auto px-4">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center space-x-4">
          <button 
            @click="navigateTo('/profile/' + currentUser.id)"
            class="text-gray-600 hover:text-gray-900"
          >
            <ArrowLeftIcon class="w-6 h-6" />
          </button>
          <h1 class="text-2xl font-semibold text-gray-900">Edit Profile</h1>
        </div>
        <button 
          @click="saveProfile"
          :disabled="loading"
          class="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {{ loading ? 'Saving...' : 'Save' }}
        </button>
      </div>

      <!-- Profile Picture Section -->
      <div class="bg-white rounded-lg p-6 mb-6">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Profile Picture</h2>
        
        <div class="flex items-center space-x-6">
          <!-- Current Profile Picture -->
          <div class="relative">
            <div class="w-24 h-24 rounded-full overflow-hidden bg-gray-200">
              <img 
                v-if="form.profile_picture || currentUser.profile_picture" 
                :src="profilePicturePreview || `http://localhost:5001${currentUser.profile_picture}`" 
                :alt="currentUser.username"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full bg-gray-300 flex items-center justify-center">
                <UserIcon class="w-12 h-12 text-gray-600" />
              </div>
            </div>
            
            <!-- Delete Button -->
            <button 
              v-if="form.profile_picture || currentUser.profile_picture"
              @click="deleteProfilePicture"
              class="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
              title="Delete profile picture"
            >
              <XMarkIcon class="w-4 h-4" />
            </button>
          </div>

          <!-- Upload Button -->
          <div class="flex-1">
            <label 
              for="profile-picture" 
              class="cursor-pointer inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              <PhotoIcon class="w-4 h-4 mr-2" />
              Change Photo
            </label>
            <input 
              id="profile-picture"
              type="file"
              accept="image/*"
              @change="handleProfilePictureChange"
              class="hidden"
            />
            <p class="text-sm text-gray-500 mt-2">
              JPG, PNG or GIF. Max 5MB.
            </p>
          </div>
        </div>
      </div>

      <!-- Profile Information -->
      <div class="bg-white rounded-lg p-6">
        <h2 class="text-lg font-medium text-gray-900 mb-4">Profile Information</h2>
        
        <div class="space-y-6">
          <!-- Username -->
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              required
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              :class="{ 'border-red-500': errors.username }"
              placeholder="Enter username"
            />
            <p v-if="errors.username" class="mt-1 text-sm text-red-600">
              {{ errors.username }}
            </p>
          </div>

          <!-- Bio -->
          <div>
            <label for="bio" class="block text-sm font-medium text-gray-700 mb-2">
              Bio
            </label>
            <textarea
              id="bio"
              v-model="form.bio"
              rows="4"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              :class="{ 'border-red-500': errors.bio }"
              placeholder="Tell us about yourself..."
            ></textarea>
            <p v-if="errors.bio" class="mt-1 text-sm text-red-600">
              {{ errors.bio }}
            </p>
            <p class="text-sm text-gray-500 mt-1">
              {{ form.bio?.length || 0 }}/150 characters
            </p>
          </div>
        </div>
      </div>

      <!-- Error Message -->
      <div v-if="error" class="mt-6 bg-red-50 border border-red-200 rounded-md p-4">
        <p class="text-sm text-red-600">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { 
  ArrowLeftIcon, 
  UserIcon, 
  PhotoIcon, 
  XMarkIcon 
} from '@heroicons/vue/24/outline'

// State
const loading = ref(false)
const error = ref('')
const currentUser = ref({})
const profilePicturePreview = ref(null)
const form = reactive({
  username: '',
  bio: '',
  profile_picture: null
})
const errors = reactive({
  username: '',
  bio: ''
})

// Load current user data
onMounted(() => {
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  currentUser.value = user
  
  // Initialize form with current values
  form.username = user.username || ''
  form.bio = user.bio || ''
})

// Handle profile picture change
const handleProfilePictureChange = (event) => {
  const file = event.target.files[0]
  if (!file) return

  // Validate file size (5MB)
  if (file.size > 5 * 1024 * 1024) {
    error.value = 'File size must be less than 5MB'
    return
  }

  // Validate file type
  if (!file.type.startsWith('image/')) {
    error.value = 'Please select a valid image file'
    return
  }

  // Create preview
  const reader = new FileReader()
  reader.onload = (e) => {
    profilePicturePreview.value = e.target.result
  }
  reader.readAsDataURL(file)

  form.profile_picture = file
  error.value = ''
}

// Delete profile picture
const deleteProfilePicture = () => {
  form.profile_picture = null
  profilePicturePreview.value = null
  // Set a flag to indicate deletion
  form.delete_profile_picture = true
}

// Validate form
const validateForm = () => {
  errors.username = ''
  errors.bio = ''
  
  if (!form.username.trim()) {
    errors.username = 'Username is required'
    return false
  }
  
  if (form.username.length < 3) {
    errors.username = 'Username must be at least 3 characters'
    return false
  }
  
  if (form.username.length > 30) {
    errors.username = 'Username must be less than 30 characters'
    return false
  }
  
  if (form.bio && form.bio.length > 150) {
    errors.bio = 'Bio must be less than 150 characters'
    return false
  }
  
  return true
}

// Save profile
const saveProfile = async () => {
  if (!validateForm()) return
  
  loading.value = true
  error.value = ''
  
  try {
    const token = localStorage.getItem('token')
    const formData = new FormData()
    
    formData.append('username', form.username.trim())
    formData.append('bio', form.bio?.trim() || '')
    
    if (form.profile_picture) {
      formData.append('profile_picture', form.profile_picture)
    }
    
    if (form.delete_profile_picture) {
      formData.append('delete_profile_picture', 'true')
    }
    
    const response = await fetch('http://localhost:5001/api/users/profile', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })
    
    const data = await response.json()
    
    if (response.ok) {
      // Update local storage
      const updatedUser = { ...currentUser.value, ...data.user }
      localStorage.setItem('user', JSON.stringify(updatedUser))
      currentUser.value = updatedUser
      
      // Navigate back to profile
      await navigateTo('/profile/' + currentUser.value.id)
    } else {
      error.value = data.error || 'Failed to update profile'
    }
  } catch (err) {
    error.value = 'Network error. Please try again.'
    console.error('Update profile error:', err)
  } finally {
    loading.value = false
  }
}
</script> 