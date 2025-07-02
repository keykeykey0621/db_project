<template>
  <div class="login-page">
    <h1 class="login-title">教务系统</h1>
    <div class="login-container">
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="username">账号</label>
          <input v-model="username" id="username" type="text" required />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input v-model="password" id="password" type="password" required />
        </div>
        <button type="submit">登录</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')

const handleLogin = async () => {
  try {
    const response = await axios.post('http://localhost:5000/api/login', {
      username: username.value,
      password: password.value,
    })
    if (response.data.success) {
      const role = response.data.role
      localStorage.setItem('user_id', response.data.user_id)
      if (role === 'admin') {
        router.push('/admin-dashboard')
      } else if (role === 'teacher') {
        router.push('/teacher-dashboard')
      } else if (role === 'student') {
        router.push('/student-dashboard')
      } else {
        alert('未知角色，无法跳转')
      }
    } else {
      error.value = '账号或密码错误'
      alert('登录失败，账号或密码错误')
    }
  } catch (err) {
    error.value = '账号或密码错误'
    alert('登录失败，账号或密码错误')
  }
}
</script>

<style scoped>
.login-title {
  margin-top: 100px;
  font-size: 40px;
  font-weight: bold;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.4);

  text-align: center;
  width: 100%;
}

text {
  display: block;
  font-family: "Microsoft YaHei", sans-serif;
  font-size: 16px;
  color: #f5f6f7;
  margin-bottom: 5px;
}

.login-page {
  height: 100vh;
  background-image: url('@/assets/login.png');
  background-size: cover;
  background-repeat: no-repeat;
  background-position: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.login-container {
  max-width: 400px;
  margin: 100px auto;
  padding: 100px;
  border: 1px solid #070606;
  border-radius: 8px;
}
.form-group {
  display: flex;              
  align-items: center;        
  margin-bottom: 16px;
}

.form-group label {
  width: 60px;                
  margin-right: 10px;
  font-size: 20px;
  color: #050505;
}

.form-group input {
  flex: 1;                    
  padding: 8px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

input {
  width: 100%;
  padding: 10px;
  box-sizing: border-box;
}
button {
  width: 100%;
  padding: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>
