<template>
  <div class="store-products">
    <h2>{{ store?.name }} - 产品管理</h2>
    <el-button type="primary" @click="showCreateProductDialog">新增产品</el-button>
    
    <!-- 产品列表 -->
    <el-table :data="products" v-loading="loading">
      <el-table-column prop="product_name" label="产品名称" />
      <el-table-column prop="sku" label="SKU" />
      <el-table-column prop="inventory" label="库存" />
      <el-table-column prop="selling_price" label="售价" />
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button size="small" @click="editProduct(row)">编辑</el-button>
          <el-button size="small" type="danger" @click="deleteProduct(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  store: {
    type: Object,
    required: true
  }
})

const loading = ref(false)
const products = ref([])

const loadProducts = async () => {
  // 加载产品列表
}

const showCreateProductDialog = () => {
  // 显示新增产品对话框
}

const editProduct = (product) => {
  // 编辑产品
}

const deleteProduct = (product) => {
  // 删除产品
}

onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.store-products {
  padding: 20px;
}
</style>
