<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-2xl mx-auto px-4">
      <!-- Header -->
      <div class="flex items-center justify-between mb-8">
        <div class="flex items-center space-x-4">
          <button 
            @click="navigateTo('/')"
            class="text-gray-600 hover:text-gray-900"
          >
            <ArrowLeftIcon class="w-6 h-6" />
          </button>
          <h1 class="text-2xl font-semibold text-gray-900">Settings</h1>
        </div>
      </div>

      <!-- Settings Options -->
      <div class="space-y-6">
        <!-- Change Email Section -->
        <div class="bg-white rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-medium text-gray-900">Change Email</h2>
            <button 
              @click="showEmailForm = !showEmailForm"
              class="text-blue-600 hover:text-blue-700 font-medium"
            >
              {{ showEmailForm ? 'Cancel' : 'Change' }}
            </button>
          </div>
          
          <div v-if="showEmailForm" class="space-y-4">
            <div>
              <label for="new-email" class="block text-sm font-medium text-gray-700 mb-2">
                New Email
              </label>
              <input
                id="new-email"
                v-model="emailForm.email"
                type="email"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :class="{ 'border-red-500': emailErrors.email }"
                placeholder="Enter new email"
              />
              <p v-if="emailErrors.email" class="mt-1 text-sm text-red-600">
                {{ emailErrors.email }}
              </p>
            </div>

            <div>
              <label for="email-password" class="block text-sm font-medium text-gray-700 mb-2">
                Current Password
              </label>
              <input
                id="email-password"
                v-model="emailForm.password"
                type="password"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :class="{ 'border-red-500': emailErrors.password }"
                placeholder="Enter current password"
              />
              <p v-if="emailErrors.password" class="mt-1 text-sm text-red-600">
                {{ emailErrors.password }}
              </p>
            </div>

            <div>
              <label for="email-confirm-password" class="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password
              </label>
              <input
                id="email-confirm-password"
                v-model="emailForm.confirmPassword"
                type="password"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :class="{ 'border-red-500': emailErrors.confirmPassword }"
                placeholder="Confirm current password"
              />
              <p v-if="emailErrors.confirmPassword" class="mt-1 text-sm text-red-600">
                {{ emailErrors.confirmPassword }}
              </p>
            </div>

            <div v-if="emailError" class="bg-red-50 border border-red-200 rounded-md p-4">
              <p class="text-sm text-red-600">{{ emailError }}</p>
            </div>

            <div class="flex space-x-3">
              <button 
                @click="changeEmail"
                :disabled="emailLoading"
                class="px-4 py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {{ emailLoading ? 'Changing...' : 'Change Email' }}
              </button>
              <button 
                @click="cancelEmailChange"
                class="px-4 py-2 bg-gray-200 text-gray-700 rounded-md font-medium hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>

        <!-- Change Password Section -->
        <div class="bg-white rounded-lg p-6">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-lg font-medium text-gray-900">Change Password</h2>
            <button 
              @click="showPasswordForm = !showPasswordForm"
              class="text-blue-600 hover:text-blue-700 font-medium"
            >
              {{ showPasswordForm ? 'Cancel' : 'Change' }}
            </button>
          </div>
          
          <div v-if="showPasswordForm" class="space-y-4">
            <div>
              <label for="old-password" class="block text-sm font-medium text-gray-700 mb-2">
                Current Password
              </label>
              <input
                id="old-password"
                v-model="passwordForm.oldPassword"
                type="password"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :class="{ 'border-red-500': passwordErrors.oldPassword }"
                placeholder="Enter current password"
              />
              <p v-if="passwordErrors.oldPassword" class="mt-1 text-sm text-red-600">
                {{ passwordErrors.oldPassword }}
              </p>
            </div>

            <div>
              <label for="new-password" class="block text-sm font-medium text-gray-700 mb-2">
                New Password
              </label>
              <input
                id="new-password"
                v-model="passwordForm.newPassword"
                type="password"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :class="{ 'border-red-500': passwordErrors.newPassword }"
                placeholder="Enter new password"
              />
              <p v-if="passwordErrors.newPassword" class="mt-1 text-sm text-red-600">
                {{ passwordErrors.newPassword }}
              </p>
            </div>

            <div>
              <label for="confirm-new-password" class="block text-sm font-medium text-gray-700 mb-2">
                Confirm New Password
              </label>
              <input
                id="confirm-new-password"
                v-model="passwordForm.confirmPassword"
                type="password"
                required
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                :class="{ 'border-red-500': passwordErrors.confirmPassword }"
                placeholder="Confirm new password"
              />
              <p v-if="passwordErrors.confirmPassword" class="mt-1 text-sm text-red-600">
                {{ passwordErrors.confirmPassword }}
              </p>
            </div>

            <div v-if="passwordError" class="bg-red-50 border border-red-200 rounded-md p-4">
              <p class="text-sm text-red-600">{{ passwordError }}</p>
            </div>

            <div class="flex space-x-3">
              <button 
                @click="changePassword"
                :disabled="passwordLoading"
                class="px-4 py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {{ passwordLoading ? 'Changing...' : 'Change Password' }}
              </button>
              <button 
                @click="cancelPasswordChange"
                class="px-4 py-2 bg-gray-200 text-gray-700 rounded-md font-medium hover:bg-gray-300 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ArrowLeftIcon } from '@heroicons/vue/24/outline'

// State
const showEmailForm = ref(false)
const showPasswordForm = ref(false)
const emailLoading = ref(false)
const passwordLoading = ref(false)
const emailError = ref('')
const passwordError = ref('')

// Email form
const emailForm = reactive({
  email: '',
  password: '',
  confirmPassword: ''
})

const emailErrors = reactive({
  email: '',
  password: '',
  confirmPassword: ''
})

// Password form
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordErrors = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// Validate email form
const validateEmailForm = () => {
  emailErrors.email = ''
  emailErrors.password = ''
  emailErrors.confirmPassword = ''
  
  if (!emailForm.email.trim()) {
    emailErrors.email = 'Email is required'
    return false
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(emailForm.email)) {
    emailErrors.email = 'Please enter a valid email'
    return false
  }
  
  if (!emailForm.password) {
    emailErrors.password = 'Password is required'
    return false
  }
  
  if (!emailForm.confirmPassword) {
    emailErrors.confirmPassword = 'Please confirm your password'
    return false
  }
  
  if (emailForm.password !== emailForm.confirmPassword) {
    emailErrors.confirmPassword = 'Passwords do not match'
    return false
  }
  
  return true
}

// Validate password form
const validatePasswordForm = () => {
  passwordErrors.oldPassword = ''
  passwordErrors.newPassword = ''
  passwordErrors.confirmPassword = ''
  
  if (!passwordForm.oldPassword) {
    passwordErrors.oldPassword = 'Current password is required'
    return false
  }
  
  if (!passwordForm.newPassword) {
    passwordErrors.newPassword = 'New password is required'
    return false
  }
  
  if (passwordForm.newPassword.length < 6) {
    passwordErrors.newPassword = 'Password must be at least 6 characters'
    return false
  }
  
  if (!passwordForm.confirmPassword) {
    passwordErrors.confirmPassword = 'Please confirm your new password'
    return false
  }
  
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordErrors.confirmPassword = 'Passwords do not match'
    return false
  }
  
  return true
}

// Change email
const changeEmail = async () => {
  if (!validateEmailForm()) return
  
  emailLoading.value = true
  emailError.value = ''
  
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('http://localhost:5001/api/users/change-email', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        email: emailForm.email.trim(),
        password: emailForm.password
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      // Update local storage
      const user = JSON.parse(localStorage.getItem('user') || '{}')
      user.email = emailForm.email.trim()
      localStorage.setItem('user', JSON.stringify(user))
      
      // Reset form
      emailForm.email = ''
      emailForm.password = ''
      emailForm.confirmPassword = ''
      showEmailForm.value = false
      
      // Show success message (you could add a toast notification here)
      alert('Email changed successfully!')
    } else {
      emailError.value = data.error || 'Failed to change email'
    }
  } catch (err) {
    emailError.value = 'Network error. Please try again.'
    console.error('Change email error:', err)
  } finally {
    emailLoading.value = false
  }
}

// Change password
const changePassword = async () => {
  if (!validatePasswordForm()) return
  
  passwordLoading.value = true
  passwordError.value = ''
  
  try {
    const token = localStorage.getItem('token')
    const response = await fetch('http://localhost:5001/api/users/change-password', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        old_password: passwordForm.oldPassword,
        new_password: passwordForm.newPassword
      })
    })
    
    const data = await response.json()
    
    if (response.ok) {
      // Reset form
      passwordForm.oldPassword = ''
      passwordForm.newPassword = ''
      passwordForm.confirmPassword = ''
      showPasswordForm.value = false
      
      // Show success message
      alert('Password changed successfully!')
    } else {
      passwordError.value = data.error || 'Failed to change password'
    }
  } catch (err) {
    passwordError.value = 'Network error. Please try again.'
    console.error('Change password error:', err)
  } finally {
    passwordLoading.value = false
  }
}

// Cancel email change
const cancelEmailChange = () => {
  showEmailForm.value = false
  emailForm.email = ''
  emailForm.password = ''
  emailForm.confirmPassword = ''
  emailError.value = ''
  emailErrors.email = ''
  emailErrors.password = ''
  emailErrors.confirmPassword = ''
}

// Cancel password change
const cancelPasswordChange = () => {
  showPasswordForm.value = false
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
  passwordError.value = ''
  passwordErrors.oldPassword = ''
  passwordErrors.newPassword = ''
  passwordErrors.confirmPassword = ''
}
</script> 