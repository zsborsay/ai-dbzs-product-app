<template>
  <div class="mini-cart-panel">
    <div class="mini-cart-header">🛒 Cart</div>
    <div v-if="cartItems.length === 0" class="mini-cart-empty">Cart is empty.</div>
    <div v-else class="mini-cart-list">
      <div v-for="item in normalizedItems" :key="item.id" class="mini-cart-item">
        <span class="mini-cart-name">{{ item.name }}</span>
        <span class="mini-cart-unit">${{ item.price.toFixed(2) }}</span>
        <span class="mini-cart-qty">x{{ item.quantity }}</span>
        <span class="mini-cart-line-total">${{ (item.price * item.quantity).toFixed(2) }}</span>
      </div>
      <div class="mini-cart-total-row">
        <span class="mini-cart-total-label">Total:</span>
        <span class="mini-cart-total-value">${{ cartTotal.toFixed(2) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, defineProps } from 'vue'
const props = defineProps({
  cartItems: {
    type: Array,
    default: () => []
  }
})
// Normalize items to support both local UI shape and backend API shape { product: { name, price }, quantity }
const normalizedItems = computed(() => {
  return (props.cartItems || []).map((item) => {
    const price = Number(item?.price ?? item?.product?.price ?? 0)
    const name = item?.name ?? item?.product?.name ?? 'Unknown'
    const quantity = Number(item?.quantity ?? 0)
    return {
      id: item.id ?? `${item.product_id || name}`,
      name,
      price,
      quantity,
    }
  })
})

const cartTotal = computed(() => {
  return normalizedItems.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
})
</script>

<style scoped>
.mini-cart-panel {
  position: fixed;
  bottom: 24px;
  left: 24px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
  padding: 18px 22px 14px 22px;
  min-width: 260px;
  z-index: 1000;
  font-family: Inter, sans-serif;
}
.mini-cart-header {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 10px;
}
.mini-cart-list {
  margin-bottom: 8px;
}
.mini-cart-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  margin-bottom: 4px;
}
.mini-cart-name {
  flex: 2;
}
.mini-cart-unit {
  flex: 1;
  text-align: right;
}
.mini-cart-qty {
  flex: 1;
  text-align: right;
}
.mini-cart-line-total {
  flex: 1;
  text-align: right;
  font-weight: 500;
}
.mini-cart-total-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  font-weight: 600;
  border-top: 1px solid #eee;
  padding-top: 6px;
}
.mini-cart-total-label {
  color: #717182;
}
.mini-cart-total-value {
  color: #030213;
}
.mini-cart-empty {
  color: #717182;
  font-size: 13px;
  text-align: center;
}
</style>
