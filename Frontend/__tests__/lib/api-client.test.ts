import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import axios from 'axios'

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      interceptors: {
        request: {
          use: vi.fn()
        },
        response: {
          use: vi.fn()
        }
      },
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn()
    }))
  }
}))

describe('API Client Configuration', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Clear localStorage after each test
    localStorage.clear()
  })

  it('should have correct environment variables', () => {
    expect(process.env.NEXT_PUBLIC_API_URL).toBe('http://localhost:8000')
    expect(process.env.NEXT_PUBLIC_APP_NAME).toBe('ruleIQ')
  })

  it('should create axios instance when imported', async () => {
    // Import the module to trigger axios.create
    await import('../../app/lib/api-client')

    expect(axios.create).toHaveBeenCalledWith({
      baseURL: 'http://localhost:8000/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      withCredentials: false
    })
  })

  it('should handle localStorage operations', () => {
    // Test localStorage mock is working
    const testKey = 'test'
    const testValue = 'value'

    // Set item
    localStorage.setItem(testKey, testValue)

    // Get item - localStorage mock should work
    const retrievedValue = localStorage.getItem(testKey)
    expect(retrievedValue).toBe(testValue)

    // Remove item
    localStorage.removeItem(testKey)
    expect(localStorage.getItem(testKey)).toBeNull()
  })

  it('should have proper axios mock setup', () => {
    expect(axios.create).toBeDefined()
    expect(typeof axios.create).toBe('function')
  })
})
