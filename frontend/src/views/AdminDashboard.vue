<template>
  <div class="admin-dashboard">
    <aside class="sidebar">
      <div class="logo">教务系统</div>
      <ul>
        <li :class="{active: activeMenu==='account'}" @click="activeMenu='account'">账号信息</li>
        <li :class="{active: activeMenu==='add'}" @click="activeMenu='add'">添加账号</li>
        <li :class="{active: activeMenu==='college'}" @click="activeMenu='college'">添加学院</li>
        <li :class="{active: activeMenu==='class'}" @click="activeMenu='class'">添加班级</li>
        <li @click="logout" class="logout">退出登录</li>
      </ul>
    </aside>
    <main class="main-content">
      <transition name="fade" mode="out-in">
        <!-- 账号信息 -->
        <div v-if="activeMenu==='account'" key="account">
          <form class="account-form" @submit.prevent="changePassword">
            <div class="form-row">
              <label for="admin-id">管理员号码：</label>
              <input id="admin-id" type="text" :value="admin.id" readonly />
            </div>
            <div class="form-row password-row">
              <div class="password-group">
                <label for="old-password">原始密码：</label>
                <input id="old-password" v-model="oldPassword" type="password" placeholder="输入原始密码" />
              </div>
              <span class="arrow">→</span>
              <div class="password-group">
                <label for="new-password">新密码：</label>
                <input id="new-password" v-model="newPassword" type="password" placeholder="输入新密码" />
              </div>
              <button type="submit">修改</button>
            </div>
            <div v-if="passwordMsg" class="password-msg">{{ passwordMsg }}</div>
          </form>
        </div>
        <!-- 添加账号板块 -->
        <div v-else-if="activeMenu==='add'" key="add" class="add-account-panel">
          <div class="account-manage-header">
            <input v-model="searchKeyword" @input="fetchAccounts" placeholder="搜索账号..." class="search-input" />
            <button class="add-btn" @click="showAddDialog = true">添加账号</button>
          </div>
          <div class="account-list">
            <div v-for="item in accounts" :key="item.id" class="account-item">
              <span class="account-id">{{ item.id }}</span>
              <span class="account-role">{{ roleMap[item.role] || item.role }}</span>
              <button class="edit-btn" @click="openChangePwd(item)">修改密码</button>
              <button class="del-btn" @click="openDelete(item)">删除</button>
            </div>
            <div v-if="accounts.length === 0" class="empty-tip">暂无账号</div>
          </div>
          <!-- 修改密码弹窗 -->
          <div v-if="showPwdDialog" class="dialog-mask">
            <div class="dialog">
              <h3>修改密码</h3>
              <div>账号：{{ selectedAccount.id }}</div>
              <input v-model="newPwd" type="password" placeholder="新密码" />
              <div class="dialog-actions">
                <button @click="changePwd">确认</button>
                <button @click="showPwdDialog = false">取消</button>
              </div>
              <div v-if="pwdMsg" class="dialog-msg">{{ pwdMsg }}</div>
            </div>
          </div>
          <!-- 删除账号弹窗 -->
          <div v-if="showDelDialog" class="dialog-mask">
            <div class="dialog">
              <h3>确认删除</h3>
              <div>确定要删除账号 <b>{{ selectedAccount.id }}</b> 吗？</div>
              <div class="dialog-actions">
                <button @click="deleteAccount">确认</button>
                <button @click="showDelDialog = false">取消</button>
              </div>
              <div v-if="delMsg" class="dialog-msg">{{ delMsg }}</div>
            </div>
          </div>
          <!-- 添加账号弹窗 -->
          <div v-if="showAddDialog" class="dialog-mask">
            <div class="dialog">
              <h3>添加账号</h3>
              <div>
                <label>职责：</label>
                <select v-model="addRole">
                  <option value="admin">管理员</option>
                  <option value="teacher">教师</option>
                  <option value="student">学生</option>
                </select>
              </div>
              <div v-if="addRole !== 'admin'">
                <label>姓名：</label>
                <input v-model="addName" placeholder="请输入姓名" />
              </div>
              <div>
                <label>账号：</label>
                <span class="prefix">{{ getPrefix(addRole) }}</span>
                <input v-model="addIdSuffix" placeholder="请输入账号后缀" />
              </div>
              <div>
                <label>密码：</label>
                <input v-model="addPwd" type="password" placeholder="密码" />
              </div>
              <div class="dialog-actions">
                <button @click="addAccount">确认</button>
                <button @click="showAddDialog = false">取消</button>
              </div>
              <div v-if="addMsg" class="dialog-msg">{{ addMsg }}</div>
            </div>
          </div>
        </div>
        <!-- 添加学院板块，结构与添加账号一致，带表头 -->
        <div v-else-if="activeMenu==='college'" key="college" class="add-account-panel">
          <div class="account-manage-header">
            <input v-model="collegeSearchKeyword" @input="fetchColleges" placeholder="搜索学院..." class="search-input" />
            <button class="add-btn" @click="showAddCollegeDialog = true">添加学院</button>
          </div>
          <div class="account-list">
            <!-- 表头 -->
            <div class="account-item" style="font-weight:bold;background:rgba(93,173,226,0.10);">
              <span class="account-id">学院号</span>
              <span class="account-role">学院名</span>
              <span class="account-role">联系方式</span>
              <span style="width:120px"></span>
            </div>
            <!-- 数据行 -->
            <div v-for="item in colleges" :key="item.college_id" class="account-item">
              <span class="account-id">{{ item.college_id }}</span>
              <span class="account-role">{{ item.name }}</span>
              <span class="account-role">{{ item.contact }}</span>
              <button class="edit-btn" @click="openEditCollege(item)">修改</button>
              <button class="del-btn" @click="openDeleteCollege(item)">删除</button>
            </div>
            <div v-if="colleges.length === 0" class="empty-tip">暂无学院</div>
          </div>
          <!-- 添加学院弹窗 -->
          <div v-if="showAddCollegeDialog" class="dialog-mask">
            <div class="dialog">
              <h3>添加学院</h3>
              <div>
                <label>学院号：</label>
                <input v-model="addCollegeId" placeholder="学院号" />
              </div>
              <div>
                <label>学院名：</label>
                <input v-model="addCollegeName" placeholder="学院名" />
              </div>
              <div>
                <label>联系方式：</label>
                <input v-model="addCollegeContact" placeholder="联系方式" />
              </div>
              <div class="dialog-actions">
                <button @click="addCollege">确认</button>
                <button @click="showAddCollegeDialog = false">取消</button>
              </div>
              <div v-if="addCollegeMsg" class="dialog-msg">{{ addCollegeMsg }}</div>
            </div>
          </div>
          <!-- 修改学院弹窗 -->
          <div v-if="showEditCollegeDialog" class="dialog-mask">
            <div class="dialog">
              <h3>修改学院信息</h3>
              <div>
                <label>学院号：</label>
                <input v-model="editCollegeId" placeholder="学院号" disabled />
              </div>
              <div>
                <label>学院名：</label>
                <input v-model="editCollegeName" placeholder="学院名" />
              </div>
              <div>
                <label>联系方式：</label>
                <input v-model="editCollegeContact" placeholder="联系方式" />
              </div>
              <div class="dialog-actions">
                <button @click="editCollege">保存</button>
                <button @click="showEditCollegeDialog = false">取消</button>
              </div>
              <div v-if="editCollegeMsg" class="dialog-msg">{{ editCollegeMsg }}</div>
            </div>
          </div>
          <!-- 删除学院弹窗 -->
          <div v-if="showDelCollegeDialog" class="dialog-mask">
            <div class="dialog">
              <h3>确认删除</h3>
              <div>确定要删除学院 <b>{{ delCollegeId }}</b> 吗？</div>
              <div class="dialog-actions">
                <button @click="deleteCollege">确认</button>
                <button @click="showDelCollegeDialog = false">取消</button>
              </div>
              <div v-if="delCollegeMsg" class="dialog-msg">{{ delCollegeMsg }}</div>
            </div>
          </div>
        </div>
        <!-- 添加班级板块，结构与添加账号/学院一致，带表头 -->
        <div v-else-if="activeMenu==='class'" key="class" class="add-account-panel">
          <div class="account-manage-header">
            <input v-model="classSearchKeyword" @input="fetchClasses" placeholder="搜索班级..." class="search-input" />
            <button class="add-btn" @click="showAddClassDialog = true">添加班级</button>
          </div>
          <div class="account-list">
            <!-- 表头 -->
            <div class="account-item" style="font-weight:bold;background:rgba(93,173,226,0.10);">
              <span class="account-id">班级号</span>
              <span class="account-role">班级名</span>
              <span class="account-role">所属学院</span>
              <span style="width:120px"></span>
            </div>
            <!-- 数据行 -->
            <div v-for="item in classes" :key="item.class_id" class="account-item">
              <span class="account-id">{{ item.class_id }}</span>
              <span class="account-role">{{ item.name }}</span>
              <span class="account-role">{{ getCollegeName(item.college_id) }}</span>
              <button class="edit-btn" @click="openEditClass(item)">修改</button>
              <button class="del-btn" @click="openDeleteClass(item)">删除</button>
            </div>
            <div v-if="classes.length === 0" class="empty-tip">暂无班级</div>
          </div>
          <!-- 添加班级弹窗 -->
          <div v-if="showAddClassDialog" class="dialog-mask">
            <div class="dialog">
              <h3>添加班级</h3>
              <div>
                <label>班级号：</label>
                <input v-model="addClassId" placeholder="班级号" />
              </div>
              <div>
                <label>班级名：</label>
                <input v-model="addClassName" placeholder="班级名" />
              </div>
              <div>
                <label>所属学院：</label>
                <select v-model="addClassCollegeId">
                  <option value="">请选择学院</option>
                  <option v-for="college in colleges" :key="college.college_id" :value="college.college_id">
                    {{ college.name }}
                  </option>
                </select>
              </div>
              <div class="dialog-actions">
                <button @click="addClass">确认</button>
                <button @click="showAddClassDialog = false">取消</button>
              </div>
              <div v-if="addClassMsg" class="dialog-msg">{{ addClassMsg }}</div>
            </div>
          </div>
          <!-- 修改班级弹窗 -->
          <div v-if="showEditClassDialog" class="dialog-mask">
            <div class="dialog">
              <h3>修改班级信息</h3>
              <div>
                <label>班级号：</label>
                <input v-model="editClassId" placeholder="班级号" disabled />
              </div>
              <div>
                <label>班级名：</label>
                <input v-model="editClassName" placeholder="班级名" />
              </div>
              <div>
                <label>所属学院：</label>
                <select v-model="editClassCollegeId">
                  <option value="">请选择学院</option>
                  <option v-for="college in colleges" :key="college.college_id" :value="college.college_id">
                    {{ college.name }}
                  </option>
                </select>
              </div>
              <div class="dialog-actions">
                <button @click="editClass">保存</button>
                <button @click="showEditClassDialog = false">取消</button>
              </div>
              <div v-if="editClassMsg" class="dialog-msg">{{ editClassMsg }}</div>
            </div>
          </div>
          <!-- 删除班级弹窗 -->
          <div v-if="showDelClassDialog" class="dialog-mask">
            <div class="dialog">
              <h3>确认删除</h3>
              <div>确定要删除班级 <b>{{ delClassId }}</b> 吗？</div>
              <div class="dialog-actions">
                <button @click="deleteClass">确认</button>
                <button @click="showDelClassDialog = false">取消</button>
              </div>
              <div v-if="delClassMsg" class="dialog-msg">{{ delClassMsg }}</div>
            </div>
          </div>
        </div>
      </transition>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const activeMenu = ref('account')

// 账号信息相关
const admin = ref({ id: '', password: '' })
const oldPassword = ref('')
const newPassword = ref('')
const passwordMsg = ref('')

const fetchAdminInfo = async () => {
  try {
    const userId = localStorage.getItem('user_id')
    if (!userId) {
      passwordMsg.value = '未登录'
      return
    }
    const res = await axios.get('http://localhost:5000/api/admin/info', {
      params: { id: userId }
    })
    if (res.data.success) {
      admin.value.id = res.data.id
    }
  } catch (e) {
    passwordMsg.value = '获取账号信息失败'
  }
}

const changePassword = async () => {
  if (!oldPassword.value) {
    passwordMsg.value = '请输入原始密码'
    return
  }
  if (!newPassword.value) {
    passwordMsg.value = '请输入新密码'
    return
  }
  try {
    const res = await axios.post('http://localhost:5000/api/account/change_password', {
      id: admin.value.id,
      old_password: oldPassword.value,
      new_password: newPassword.value
    })
    if (res.data.success) {
      passwordMsg.value = '密码修改成功'
      admin.value.password = res.data.password
      oldPassword.value = ''
      newPassword.value = ''
    } else {
      passwordMsg.value = res.data.message || '密码修改失败'
    }
  } catch (e) {
    passwordMsg.value = '密码修改失败'
  }
}

function logout() {
  localStorage.removeItem('user_id')
  router.push('/')
}

// 添加账号相关
const searchKeyword = ref('')
const accounts = ref([])
const showPwdDialog = ref(false)
const showDelDialog = ref(false)
const showAddDialog = ref(false)
const selectedAccount = ref({})
const newPwd = ref('')
const pwdMsg = ref('')
const delMsg = ref('')
const addRole = ref('admin')
const addIdSuffix = ref('')
const addPwd = ref('')
const addMsg = ref('')
const addName = ref('')

const roleMap = { admin: '管理员', teacher: '教师', student: '学生' }

const getPrefix = (role) => {
  if (role === 'admin') return 'A'
  if (role === 'teacher') return 'T'
  if (role === 'student') return 'S'
  return ''
}

const fetchAccounts = async () => {
  const res = await axios.get('http://localhost:5000/api/admin/accounts', {
    params: { keyword: searchKeyword.value, exclude_id: admin.value.id }
  })
  if (res.data.success) accounts.value = res.data.accounts
}

const openChangePwd = (item) => {
  selectedAccount.value = item
  newPwd.value = ''
  pwdMsg.value = ''
  showPwdDialog.value = true
}
const changePwd = async () => {
  if (!newPwd.value) {
    pwdMsg.value = '请输入新密码'
    return
  }
  const res = await axios.post('http://localhost:5000/api/admin/account/change_password', {
    id: selectedAccount.value.id,
    new_password: newPwd.value
  })
  if (res.data.success) {
    pwdMsg.value = '修改成功'
    setTimeout(() => { showPwdDialog.value = false }, 800)
    fetchAccounts()
  } else {
    pwdMsg.value = res.data.message || '修改失败'
  }
}

const openDelete = (item) => {
  selectedAccount.value = item
  delMsg.value = ''
  showDelDialog.value = true
}
const deleteAccount = async () => {
  const res = await axios.post('http://localhost:5000/api/admin/account/delete', {
    id: selectedAccount.value.id
  })
  if (res.data.success) {
    delMsg.value = '删除成功'
    fetchAccounts()
    setTimeout(() => { showDelDialog.value = false }, 800)
  } else {
    delMsg.value = res.data.message || '删除失败'
  }
}

const addAccount = async () => {
  if (!addIdSuffix.value || !addPwd.value) {
    addMsg.value = '请填写账号和密码'
    return
  }
  if (addRole.value !== 'admin' && !addName.value) {
    addMsg.value = '请填写姓名'
    return
  }
  const prefix = getPrefix(addRole.value)
  const fullId = prefix + addIdSuffix.value
  // 账号开头校验
  if ((addRole.value === 'admin' && !fullId.startsWith('A')) ||
      (addRole.value === 'teacher' && !fullId.startsWith('T')) ||
      (addRole.value === 'student' && !fullId.startsWith('S'))) {
    addMsg.value = '账号开头与职责不符'
    return
  }
  const payload = {
    id: fullId,
    password: addPwd.value,
    role: addRole.value,
  }
  if (addRole.value !== 'admin') {
    payload.name = addName.value
  }
  const res = await axios.post('http://localhost:5000/api/admin/account/add', payload)
  if (res.data.success) {
    addMsg.value = '添加成功'
    fetchAccounts()
    setTimeout(() => { showAddDialog.value = false }, 800)
    addIdSuffix.value = ''
    addPwd.value = ''
    addName.value = ''
  } else {
    addMsg.value = res.data.message || '添加失败'
  }
}

// 学院相关
const collegeSearchKeyword = ref('')
const colleges = ref([])
const showAddCollegeDialog = ref(false)
const showEditCollegeDialog = ref(false)
const showDelCollegeDialog = ref(false)
const addCollegeId = ref('')
const addCollegeName = ref('')
const addCollegeContact = ref('')
const addCollegeMsg = ref('')
const editCollegeId = ref('')
const editCollegeName = ref('')
const editCollegeContact = ref('')
const editCollegeMsg = ref('')
const delCollegeId = ref('')
const delCollegeMsg = ref('')

// 获取学院列表
const fetchColleges = async () => {
  const res = await axios.get('http://localhost:5000/api/admin/colleges', {
    params: { keyword: collegeSearchKeyword.value }
  })
  if (res.data.success) colleges.value = res.data.colleges
}

// 添加学院
const addCollege = async () => {
  if (!addCollegeId.value || !addCollegeName.value) {
    addCollegeMsg.value = '请填写学院号和学院名'
    return
  }
  const res = await axios.post('http://localhost:5000/api/admin/college/add', {
    college_id: addCollegeId.value,
    name: addCollegeName.value,
    contact: addCollegeContact.value
  })
  if (res.data.success) {
    addCollegeMsg.value = '添加成功'
    fetchColleges()
    setTimeout(() => { showAddCollegeDialog.value = false }, 800)
    addCollegeId.value = ''
    addCollegeName.value = ''
    addCollegeContact.value = ''
  } else {
    addCollegeMsg.value = res.data.message || '添加失败'
  }
}

// 打开修改弹窗
const openEditCollege = (item) => {
  editCollegeId.value = item.college_id
  editCollegeName.value = item.name
  editCollegeContact.value = item.contact
  editCollegeMsg.value = ''
  showEditCollegeDialog.value = true
}

// 修改学院
const editCollege = async () => {
  if (!editCollegeId.value || !editCollegeName.value) {
    editCollegeMsg.value = '请填写学院号和学院名'
    return
  }
  const res = await axios.post('http://localhost:5000/api/admin/college/edit', {
    college_id: editCollegeId.value,
    name: editCollegeName.value,
    contact: editCollegeContact.value
  })
  if (res.data.success) {
    editCollegeMsg.value = '修改成功'
    fetchColleges()
    setTimeout(() => { showEditCollegeDialog.value = false }, 800)
  } else {
    editCollegeMsg.value = res.data.message || '修改失败'
  }
}

// 删除学院
const openDeleteCollege = (item) => {
  delCollegeId.value = item.college_id
  delCollegeMsg.value = ''
  showDelCollegeDialog.value = true
}
const deleteCollege = async () => {
  const res = await axios.post('http://localhost:5000/api/admin/college/delete', {
    college_id: delCollegeId.value
  })
  if (res.data.success) {
    delCollegeMsg.value = '删除成功'
    fetchColleges()
    setTimeout(() => { showDelCollegeDialog.value = false }, 800)
  } else {
    delCollegeMsg.value = res.data.message || '删除失败'
  }
}

// 班级相关
const classSearchKeyword = ref('')
const classes = ref([])
const showAddClassDialog = ref(false)
const showEditClassDialog = ref(false)
const showDelClassDialog = ref(false)
const addClassId = ref('')
const addClassName = ref('')
const addClassCollegeId = ref('')
const addClassMsg = ref('')
const editClassId = ref('')
const editClassName = ref('')
const editClassCollegeId = ref('')
const editClassMsg = ref('')
const delClassId = ref('')
const delClassMsg = ref('')

// 获取班级列表
const fetchClasses = async () => {
  const res = await axios.get('http://localhost:5000/api/admin/classes', {
    params: { keyword: classSearchKeyword.value }
  })
  if (res.data.success) classes.value = res.data.classes
}

// 获取学院名
const getCollegeName = (college_id) => {
  const college = colleges.value.find(c => c.college_id === college_id)
  return college ? college.name : college_id
}

// 添加班级
const addClass = async () => {
  if (!addClassId.value || !addClassName.value || !addClassCollegeId.value) {
    addClassMsg.value = '请填写完整信息'
    return
  }
  const res = await axios.post('http://localhost:5000/api/admin/class/add', {
    class_id: addClassId.value,
    name: addClassName.value,
    college_id: addClassCollegeId.value
  })
  if (res.data.success) {
    addClassMsg.value = '添加成功'
    fetchClasses()
    setTimeout(() => { showAddClassDialog.value = false }, 800)
    addClassId.value = ''
    addClassName.value = ''
    addClassCollegeId.value = ''
  } else {
    addClassMsg.value = res.data.message || '添加失败'
  }
}

// 打开修改弹窗
const openEditClass = (item) => {
  editClassId.value = item.class_id
  editClassName.value = item.name
  editClassCollegeId.value = item.college_id
  editClassMsg.value = ''
  showEditClassDialog.value = true
}

// 修改班级
const editClass = async () => {
  if (!editClassId.value || !editClassName.value || !editClassCollegeId.value) {
    editClassMsg.value = '请填写完整信息'
    return
  }
  const res = await axios.post('http://localhost:5000/api/admin/class/edit', {
    class_id: editClassId.value,
    name: editClassName.value,
    college_id: editClassCollegeId.value
  })
  if (res.data.success) {
    editClassMsg.value = '修改成功'
    fetchClasses()
    setTimeout(() => { showEditClassDialog.value = false }, 800)
  } else {
    editClassMsg.value = res.data.message || '修改失败'
  }
}

// 删除班级
const openDeleteClass = (item) => {
  delClassId.value = item.class_id
  delClassMsg.value = ''
  showDelClassDialog.value = true
}
const deleteClass = async () => {
  const res = await axios.post('http://localhost:5000/api/admin/class/delete', {
    class_id: delClassId.value
  })
  if (res.data.success) {
    delClassMsg.value = '删除成功'
    fetchClasses()
    setTimeout(() => { showDelClassDialog.value = false }, 800)
  } else {
    delClassMsg.value = res.data.message || '删除失败'
  }
}

// 自动刷新
onMounted(() => {
  fetchAdminInfo()
  fetchAccounts()
})
watch(activeMenu, (val) => {
  if (val === 'add') fetchAccounts()
  if (val === 'college') fetchColleges()
  if (val === 'class') {
    fetchClasses()
    fetchColleges()
  }
})
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  height: 100vh;
  background: linear-gradient(120deg, #232526 0%, #2c3e50 100%);
  font-family: 'Segoe UI', 'Arial', sans-serif;
}
.sidebar {
  width: 240px;
  background: rgba(44, 62, 80, 0.92);
  color: #eaf6fb;
  display: flex;
  flex-direction: column;
  align-items: center;
  box-shadow: 2px 0 10px rgba(0,0,0,0.12);
  padding-top: 40px;
}
.logo {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 40px;
  letter-spacing: 2px;
  color: #5dade2;
  text-shadow: 0 2px 8px #222;
}
.sidebar ul {
  list-style: none;
  padding: 0;
  width: 100%;
}
.sidebar li {
  width: 100%;
  padding: 18px 0 18px 40px;
  font-size: 20px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  border-left: 4px solid transparent;
}
.sidebar li.active, .sidebar li:hover {
  background: linear-gradient(90deg, #5dade2 0%, #232526 100%);
  color: #232526;
  border-left: 4px solid #90caf9;
}
.sidebar .logout {
  margin-top: 60px;
  color: #90caf9;
  font-weight: bold;
  border-left: 4px solid transparent;
}
.sidebar .logout:hover {
  background: #232526;
  color: #90caf9;
  border-left: 4px solid #90caf9;
}
.main-content {
  flex: 1;
  padding: 0;
  color: #eaf6fb;
  background: linear-gradient(135deg, #232526 0%, #2c3e50 100%);
  box-shadow: -2px 0 10px rgba(0,0,0,0.08);
  overflow-y: auto;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
}
.account-form {
  width: 100%;
  max-width: 700px;
  margin: 0 auto;
  font-size: 20px;
  color: #eaf6fb;
  display: flex;
  flex-direction: column;
  gap: 36px;
  justify-content: center;
}
.form-row {
  display: flex;
  align-items: center;
  gap: 18px;
  width: 100%;
}
.form-row label {
  min-width: 120px;
  color: #5dade2;
  font-weight: bold;
  font-size: 18px;
}
.form-row input[type="text"] {
  flex: 1;
  padding: 10px 14px;
  border-radius: 6px;
  border: 1px solid #5dade2;
  font-size: 18px;
  background: #232526;
  color: #eaf6fb;
  outline: none;
  box-shadow: 0 2px 8px #2c3e50;
}
.password-row {
  display: flex;
  align-items: center;
  gap: 18px;
  width: 100%;
}
.password-group {
  display: flex;
  align-items: center;
  gap: 10px;
}
.password-group label {
  min-width: 90px;
  color: #5dade2;
  font-weight: bold;
  font-size: 18px;
}
.password-group input[type="password"] {
  flex: 1;
  padding: 10px 14px;
  border-radius: 6px;
  border: 1px solid #5dade2;
  font-size: 18px;
  background: #232526;
  color: #eaf6fb;
  outline: none;
  box-shadow: 0 2px 8px #2c3e50;
}
.arrow {
  font-size: 28px;
  color: #90caf9;
  margin: 0 10px;
  font-weight: bold;
}
.password-row button {
  background: linear-gradient(90deg, #5dade2 0%, #90caf9 100%);
  color: #232526;
  border: none;
  border-radius: 6px;
  padding: 0 28px;
  font-size: 18px;
  cursor: pointer;
  transition: background 0.2s;
  font-weight: bold;
  box-shadow: 0 2px 8px #2c3e50;
  margin-left: 18px;
  height: 44px;
  line-height: 44px;
  white-space: nowrap;
  display: inline-block;
}
.password-row button:hover {
  background: linear-gradient(90deg, #90caf9 0%, #5dade2 100%);
  color: #232526;
}
.password-msg {
  margin-top: 8px;
  color: #5dade2;
  font-size: 16px;
  text-align: center;
}
.add-account-panel {
  width: 100%;
  display: flex;
  flex-direction: column;
  height: 100%;
}
.account-manage-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
  width: 100%;
}
.search-input {
  flex: 1;
  padding: 8px 14px;
  border-radius: 6px;
  border: 1px solid #5dade2;
  font-size: 18px;
  background: #232526;
  color: #eaf6fb;
}
.add-btn {
  background: linear-gradient(90deg, #5dade2 0%, #90caf9 100%);
  color: #232526;
  border: none;
  border-radius: 6px;
  padding: 8px 20px;
  font-size: 18px;
  cursor: pointer;
  font-weight: bold;
}
.account-list {
  background: rgba(44,62,80,0.85);
  border-radius: 12px;
  padding: 12px 0;
  min-height: 240px;
  width: 100%;
  flex: 1;
  overflow-y: auto;
}
.account-item {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 12px 24px;
  border-bottom: 1px solid #2c3e50;
}
.account-id { font-weight: bold; color: #5dade2; width: 160px; }
.account-role { color: #90caf9; width: 100px; }
.edit-btn, .del-btn {
  margin-left: 12px;
  padding: 4px 16px;
  border-radius: 6px;
  border: none;
  font-size: 16px;
  cursor: pointer;
}
.edit-btn { background: #90caf9; color: #232526; }
.del-btn { background: #ff7675; color: #fff; }
.empty-tip { text-align: center; color: #90caf9; padding: 32px 0; }

.dialog-mask {
  position: fixed; left: 0; top: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.35);
  display: flex; align-items: center; justify-content: center; z-index: 999;
}
.dialog {
  background: #232526;
  color: #eaf6fb;
  border-radius: 12px;
  padding: 32px 40px;
  min-width: 320px;
  box-shadow: 0 8px 32px #222a;
}
.dialog-actions {
  margin-top: 18px;
  display: flex;
  gap: 16px;
  justify-content: flex-end;
}
.dialog-msg { color: #ff7675; margin-top: 10px; }
.dialog .prefix {
  display: inline-block;
  font-weight: bold;
  color: #5dade2;
  margin-right: 4px;
  font-size: 18px;
}
</style>