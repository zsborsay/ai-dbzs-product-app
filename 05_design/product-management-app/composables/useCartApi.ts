import { ref } from 'vue'
import axios from 'axios'

const API_BASE = 'http://localhost:8000'

export function useCartApi() {
  const cartItems = ref([])
  const error = ref(null)
  const loading = ref(false)

  const fetchCart = async () => {
    loading.value = true
    try {
      const res = await axios.get(`${API_BASE}/cart/`)
      cartItems.value = res.data
    } catch (e) {
      error.value = e
    } finally {
      loading.value = false
    }
  }

  const addToCart = async (productId, quantity = 1) => {
    try {
      const res = await axios.post(`${API_BASE}/cart/`, { product_id: productId, quantity })
      return res.data
    } catch (e) {
      error.value = e
      throw e
    }
  }

  const removeFromCart = async (itemId) => {
    try {
      await axios.delete(`${API_BASE}/cart/${itemId}`)
    } catch (e) {
      error.value = e
      throw e
    }
  }

  return {
    cartItems,
    error,
    loading,
    fetchCart,
    addToCart,
    removeFromCart
  }
}
