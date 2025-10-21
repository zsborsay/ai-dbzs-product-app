<template>
  <div class="product-list">
    <div class="header-row">
      <span class="header-title">Product Management</span>
    </div>
    <div class="toolbar">
      <div class="search-container">
        <input v-model="search" type="text" placeholder="Search products..." class="search-bar" />
        <span class="search-icon">
          <img src="/assets/icons/icon-search.png" alt="search" width="20" height="20" />
        </span>
      </div>
      <button @click="showAddProduct = true" class="add-btn">
  <span class="add-icon" style="font-size: 20px; font-weight: bold; color: #fff; margin-right: 6px;">+</span>
        Add Product
      </button>
    </div>
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else>
      <div v-if="filteredProducts.length === 0" class="no-products">No products found.</div>
      <div class="product-grid">
        <div v-for="product in filteredProducts" :key="product.id" class="product-card">
          <div class="product-title-row">
            <span class="product-title">{{ product.name }}</span>
          </div>
          <div class="product-desc-row">
            <span class="product-desc">{{ product.description }}</span>
          </div>
          <div class="product-meta-row">
            <span class="product-stock">Stock: {{ product.stock }}</span>
            <span class="product-price">${{ product.price }}</span>
          </div>
          <div class="actions-row">
            <button class="action-btn view" @click="openDetails(product)">
              <span class="action-text">View</span>
              <span class="action-icon">
                <img src="/assets/icons/icon-view.png" alt="view" style="width:20px;height:20px;vertical-align:middle;display:inline-block;" />
              </span>
            </button>
            <button class="action-btn edit" @click="editProduct(product)">
              <span class="action-text">Edit</span>
              <span class="action-icon">
                <img src="/assets/icons/icon-edit.png" alt="edit" style="width:20px;height:20px;vertical-align:middle;display:inline-block;" />
              </span>
            </button>
            <button class="action-btn delete" @click="confirmDelete(product)">
              <span class="action-icon">
                <img src="/assets/icons/icon-delete.png" alt="delete" style="width:28px;height:28px;vertical-align:middle;display:inline-block;" />
              </span>
            </button>
            <button class="action-btn plus" :disabled="product.stock === 0" @click="addToCart(product)">
              <span class="action-icon" style="font-size:20px; font-weight:bold; color:#030213;">+</span>
            </button>
          </div>
        </div>
      </div>
    </div>
    <ProductDetailsDialog v-if="selectedProduct" :product="selectedProduct" @close="selectedProduct = null" />
    <ProductForm v-if="showAddProduct" @close="showAddProduct = false" @created="onProductCreated" />
    <ProductForm v-if="editingProduct" :product="editingProduct" @close="editingProduct = null" @updated="onProductUpdated" />
    <DeleteProductDialog v-if="deletingProduct" :product="deletingProduct" @close="deletingProduct = null" @deleted="onProductDeleted" />
    <MiniCartPanel :cartItems="cartItems" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useProductsApi } from '~/composables/useProductsApi'
import { useCartApi } from '~/composables/useCartApi'
import ProductDetailsDialog from './ProductDetailsDialog.vue'
import ProductForm from './ProductForm.vue'
import DeleteProductDialog from './DeleteProductDialog.vue'
import MiniCartPanel from './MiniCartPanel.vue'

const { products, loading, fetchProducts } = useProductsApi()
const { cartItems, fetchCart, addToCart: addToCartApi, error: cartError } = useCartApi()

const selectedProduct = ref(null)
const showAddProduct = ref(false)
const editingProduct = ref(null)
const deletingProduct = ref(null)
const search = ref("")

// Load cart from localStorage on mount
onMounted(() => {
  fetchProducts()
  fetchCart()
})

const filteredProducts = computed(() => {
  if (!search.value) return products.value
  return products.value.filter(p =>
    p.name.toLowerCase().includes(search.value.toLowerCase()) ||
    (p.description && p.description.toLowerCase().includes(search.value.toLowerCase()))
  )
})

function openDetails(product) {
  selectedProduct.value = product
}
function editProduct(product) {
  editingProduct.value = product
}
function confirmDelete(product) {
  deletingProduct.value = product
}
function onProductCreated() {
  showAddProduct.value = false
  fetchProducts()
}
function onProductUpdated() {
  editingProduct.value = null
  fetchProducts()
}
function onProductDeleted() {
  deletingProduct.value = null
  fetchProducts()
}

async function addToCart(product) {
  if (product.stock === 0) return;
  try {
    await addToCartApi(product.id, 1)
    await fetchProducts()
    await fetchCart()
  } catch (e) {
    if (e.response && e.response.status === 409) {
      alert('Not enough stock!')
    } else {
      alert('Error adding to cart')
    }
  }
}
</script>

<style scoped>
/* Figma pixel-perfect styles */
.product-list {
  max-width: 1120px;
  margin: 0 auto;
  padding: 21px 0 0 0;
  background: #fff;
  border-radius: 12.75px;
}
.header-row {
  margin-bottom: 32px;
}
.header-title {
  font-family: Inter, sans-serif;
  font-size: 13.2px;
  font-weight: 400;
  color: #0A0A0A;
  line-height: 21px;
  text-align: left;
  display: block;
}
.toolbar {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 32px;
  margin-bottom: 31px;
}
.search-container {
  position: relative;
  width: 392px;
}
.search-bar {
  width: 100%;
  height: 31.5px;
  padding: 0 35px 0 12px;
  border-radius: 6.75px;
  border: none;
  background: #F3F3F5;
  font-family: Inter, sans-serif;
  font-size: 10.7px;
  color: #0A0A0A;
  box-sizing: border-box;
}
.search-icon {
  position: absolute;
  right: 12px;
  top: 8px;
  width: 14px;
  height: 14px;
  display: flex;
  align-items: center;
}
.add-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #030213;
  color: #fff;
  border: none;
  border-radius: 6.75px;
  padding: 0 24px;
  height: 31.5px;
  font-family: Inter, sans-serif;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  box-shadow: none;
  transition: background 0.2s;
}
.add-btn:hover {
  background: #222;
}
.add-icon {
  display: flex;
  align-items: center;
}
.product-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}
.product-card {
  background: #fff;
  border-radius: 12.75px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  border: 1px solid rgba(0,0,0,0.1);
  padding: 15px 15px 14px 14px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 234px;
}
.product-title-row {
  margin-bottom: 0;
}
.product-title {
  font-family: Inter, sans-serif;
  font-size: 13.2px;
  font-weight: 400;
  color: #0A0A0A;
  line-height: 14px;
  display: block;
}
.product-desc-row {
  margin-bottom: 0;
}
.product-desc {
  font-family: Inter, sans-serif;
  font-size: 11.3px;
  font-weight: 400;
  color: #717182;
  line-height: 17.5px;
  display: block;
}
.product-meta-row {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.product-stock {
  font-family: Inter, sans-serif;
  font-size: 11.3px;
  color: #717182;
  font-weight: 400;
}
.product-price {
  font-family: Inter, sans-serif;
  font-size: 12.8px;
  color: #030213;
  font-weight: 500;
}
.actions-row {
  display: flex;
  flex-direction: row;
  gap: 7px;
  align-items: center;
  margin-top: 0;
}
.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 6.75px;
  font-family: Inter, sans-serif;
  font-size: 11.3px;
  font-weight: 500;
  height: 28px;
  padding: 0 12px;
  border: 1px solid rgba(0,0,0,0.1);
  background: #fff;
  color: #0A0A0A;
  cursor: pointer;
  transition: background 0.2s, border 0.2s;
}
.action-btn.view {
  border: 1px solid rgba(0,0,0,0.1);
}
.action-btn.edit {
  border: 1px solid rgba(0,0,0,0.1);
}
.action-btn.delete {
  background: #D4183D;
  border: none;
  color: #fff;
  padding: 0 12px;
}
.action-btn.plus {
  background: #007BFF;
  border: none;
  color: #fff;
  padding: 0 12px;
}
.action-btn:hover {
  background: #F3F3F5;
}
.action-btn.delete:hover {
  background: #b3122f;
}
.action-btn.plus:disabled {
  background: #A0A0A0;
  cursor: not-allowed;
}
.action-text {
  font-family: Inter, sans-serif;
  font-size: 11.3px;
  font-weight: 500;
  color: inherit;
}
.action-icon {
  display: flex;
  align-items: center;
}
</style>
