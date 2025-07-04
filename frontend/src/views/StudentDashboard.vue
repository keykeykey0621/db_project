<template>
  <div class="admin-dashboard">
    <aside class="sidebar">
      <div class="logo">教务系统</div>
      <ul>
        <li :class="{active: activeMenu==='account'}" @click="activeMenu='account'">账号信息</li>
        <li :class="{active: activeMenu==='course'}" @click="activeMenu='course'">学生选课</li>
        <li :class="{active: activeMenu==='timetable'}" @click="activeMenu='timetable'">课程表</li>
        <li @click="logout" class="logout">退出登录</li>
      </ul>
    </aside>
    <main class="main-content">
      <transition name="fade" mode="out-in">
        <div v-if="activeMenu==='account'" key="account">
          <!-- 头像区域 -->
          <div class="avatar-row">
            <img
              :src="avatarUrl"
              alt="头像"
              class="avatar-img"
              @error="onAvatarError"
            />
            <button class="avatar-upload-btn" @click="showDragModal = true">上传头像</button>
          </div>
          <!-- 拖拽上传弹窗 -->
          <div v-if="showDragModal" class="avatar-drag-modal" @click.self="showDragModal = false">
            <div
              class="avatar-drag-window"
              :class="{ 'avatar-dragover': isDragOver }"
              @dragover.prevent="onAvatarDragOver"
              @dragleave.prevent="onAvatarDragLeave"
              @drop.prevent="onAvatarDrop"
            >
              <div class="avatar-drag-title">拖拽图片到此处上传</div>
              <input type="file" id="avatarInputModal" @change="onAvatarChange" accept="image/*" class="avatar-input" />
              <label for="avatarInputModal" class="avatar-upload-btn">选择本地文件</label>
              <div class="avatar-drag-tip">支持拖拽或点击选择本地图片</div>
              <button class="avatar-cancel-btn" @click="showDragModal = false">取消</button>
            </div>
          </div>
          <!-- 账号信息表单 -->
          <form class="account-form" @submit.prevent="saveStudentInfo">
            <div class="form-row">
              <label>学号：</label>
              <input type="text" :value="student.id" readonly />
            </div>
            <div class="form-row">
              <label>姓名：</label>
              <input type="text" :value="student.name" readonly />
            </div>
            <div class="form-row">
              <label>性别：</label>
              <select v-model="editGender">
                <option value="">未填写</option>
                <option value="男">男</option>
                <option value="女">女</option>
              </select>
            </div>
            <div class="form-row">
              <label>生日：</label>
              <input type="date" v-model="editBirthday" />
            </div>
            <div class="form-row">
              <label>联系方式：</label>
              <input type="text" v-model="editContact" placeholder="请输入联系方式" />
            </div>
            <div class="form-row">
              <label>专业：</label>
              <input type="text" v-model="editMajor" placeholder="请输入专业" />
            </div>
            <div class="form-row">
              <label>班级号：</label>
              <input type="text" :value="student.class_id" readonly />
            </div>
            <div class="form-row">
              <button type="submit">保存信息</button>
            </div>
            <div v-if="infoMsg" class="password-msg">{{ infoMsg }}</div>
          </form>
          <!-- 密码修改表单 -->
          <form class="account-form" @submit.prevent="changePassword">
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
        <!-- 学生选课 -->
        <div v-else-if="activeMenu==='course'" key="course" class="add-account-panel">
          <div class="account-manage-header" style="gap: 12px;">
            <input v-model="searchCourseId" @input="fetchCoursesDebounced" placeholder="按课程号搜索..." class="search-input" style="max-width:200px;" />
            <input v-model="searchCourseName" @input="fetchCoursesDebounced" placeholder="按课程名搜索..." class="search-input" style="max-width:200px;" />
            <div style="display: flex; align-items: center; margin-left: 16px;">
              <input type="checkbox" v-model="onlyShowSelected" @change="fetchCoursesDebounced" id="onlyShowSelected" />
              <label for="onlyShowSelected" style="margin-left:4px;cursor:pointer;">只看已选课程</label>
            </div>
            <!-- 叠课申请按钮（放在选课页面搜索栏旁） -->
            <button @click="openOverlapDialog" style="margin-left:16px;">叠课申请</button>
          </div>
          <div class="account-list">
            <div class="account-item header-row">
              <span class="account-id">课程号</span>
              <span class="account-role">课程名</span>
              <span class="account-role">学分</span>
              <span class="account-role">上课地点</span>
              <span class="account-role">上课时间</span>
              <span class="account-role">任课教师</span>
              <span class="account-role">选课人数/上限</span>
              <span class="account-action"></span>
            </div>
            <div v-for="item in courses" :key="item.course_id" class="account-item">
              <span class="account-id">{{ item.course_id }}</span>
              <span class="account-role">{{ item.name }}</span>
              <span class="account-role">{{ item.credit }}</span>
              <span class="account-role">{{ item.location }}</span>
              <span class="account-role cell-wrap">{{ item.time }}</span>
              <span class="account-role">{{ getTeacherNames(item.teachers) }}</span>
              <span class="account-role">{{ item.numStudents }} / {{ item.maxStudents }}</span>
              <span class="account-action">
                <button
                  v-if="!item.selected"
                  class="add-btn"
                  @click="() => selectCourse(item.course_id, item)"
                  :title="item.numStudents >= item.maxStudents ? '人数已满' : ''"
                >选课</button>
                <button
                  v-else
                  class="del-btn"
                  @click="confirmDropCourse(item.course_id)"
                >退课</button>
              </span>
            </div>
            <div v-if="courses.length === 0" class="empty-tip">暂无课程</div>
          </div>
          <div v-if="courseMsg" class="dialog-msg">{{ courseMsg }}</div>
        </div>
        <!-- 课程表 (推荐用标准二维数组渲染) -->
        <div v-else-if="activeMenu==='timetable'" key="timetable" class="timetable-panel">
          <table class="timetable">
            <thead>
              <tr>
                <th>时段</th>
                <th>节次</th>
                <th v-for="day in timetableDays" :key="day">{{ day }}</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="(section, sidx) in timetableSections" :key="section.label">
                <!-- 分割线，除第一个section外 -->
                <tr v-if="sidx !== 0" class="section-divider">
                  <td colspan="9"></td>
                </tr>
                <tr v-for="i in section.end - section.start + 1" :key="i + '-' + section.label">
                  <td v-if="i === 1" :rowspan="section.end - section.start + 1" class="timetable-section">
                    {{ section.label }}
                  </td>
                  <td>{{ timetableTable[section.start + i - 1][0] }}</td>
                  <td v-for="(cell, j) in timetableTable[section.start + i - 1].slice(1)" :key="j" class="timetable-cell">
                    <div
                      v-for="(course, k) in cell"
                      :key="k"
                      class="course-card"
                      :class="{
                        'compressed': cell.length > 1 && hoveredCard !== `${section.start + i - 1}-${j}-${k}`,
                        'expanded': hoveredCard === `${section.start + i - 1}-${j}-${k}`
                      }"
                      @mouseenter="hoveredCard = `${section.start + i - 1}-${j}-${k}`"
                      @mouseleave="hoveredCard = null"
                    >
                      <div class="course-name">{{ course.name }}</div>
                      <div class="course-weeks">周次: {{ course.weeks_str }}</div>
                      <div class="course-location" v-if="course.location">{{ course.location }}</div>
                    </div>
                  </td>
                </tr>
              </template>
            </tbody>
          </table>
          <div v-if="!timetableTable.length" style="color:#5dade2;text-align:center;margin-top:20px;">暂无课表数据</div>
        </div>
      </transition>
    </main>

    <!-- 冲突弹窗 -->
    <div v-if="showConflictDialog" class="conflict-dialog-mask">
      <div class="conflict-dialog">
        <div class="conflict-title">选课冲突提醒</div>
        <div class="conflict-msg">该课程与您已选课程时间冲突，是否申请叠课？</div>
        <div class="conflict-actions">
          <button class="conflict-btn" @click="showConflictDialog = false">关闭</button>
          <button class="conflict-btn" @click="applyOverlap" style="background:#5dade2;color:#fff;">申请叠课</button>
        </div>
      </div>
    </div>

    <!-- 我的叠课申请弹窗 -->
    <div v-if="showOverlapDialog" class="dialog-mask">
      <div class="dialog">
        <h3>我的叠课申请</h3>
        <div v-for="app in overlapApplications" :key="app.course_id" class="overlap-row">
          <span>
            课程：{{ app.course_name }} | 状态：{{ statusText(app.status) }}
          </span>
          <button
            v-if="app.status === 'pending'"
            class="small-btn"
            @click="cancelOverlap(app.course_id)"
          >撤销</button>
        </div>
        <button @click="showOverlapDialog = false">关闭</button>
      </div>
    </div>

    <!-- 退课确认弹窗 -->
    <div v-if="showDropConfirm" class="conflict-dialog-mask">
      <div class="conflict-dialog">
        <div class="conflict-title">确认退课</div>
        <div class="conflict-msg">确定要退选该课程吗？</div>
        <div class="conflict-actions">
          <button class="conflict-btn" @click="showDropConfirm = false">取消</button>
          <button class="conflict-btn" style="background:#e74c3c;color:#fff;" @click="doDropCourse">确定退课</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const activeMenu = ref('account')
const userId = localStorage.getItem('user_id')

// 账号信息相关
const student = ref({ id: '', name: '', gender: '', birthday: '', contact: '', major: '', class_id: '' })
const oldPassword = ref('')
const newPassword = ref('')
const passwordMsg = ref('')
const editGender = ref('')
const editBirthday = ref('')
const editContact = ref('')
const editMajor = ref('')
const infoMsg = ref('')

// 头像相关
const defaultAvatar = '/assets/default_avatar.png'
const avatarUrl = ref('')
const avatarExts = ['jpg', 'png', 'jpeg', 'gif']
let avatarTryIndex = 0

function setAvatarUrl() {
  avatarTryIndex = 0
  avatarUrl.value = `/assets/${userId}/avatar.${avatarExts[avatarTryIndex]}?${Date.now()}`
}
function onAvatarError() {
  avatarTryIndex++
  if (avatarTryIndex < avatarExts.length) {
    avatarUrl.value = `/assets/${userId}/avatar.${avatarExts[avatarTryIndex]}?${Date.now()}`
  } else {
    avatarUrl.value = defaultAvatar
  }
}

// 拖拽上传弹窗相关
const showDragModal = ref(false)
const isDragOver = ref(false)
function onAvatarDragOver() {
  isDragOver.value = true
}
function onAvatarDragLeave() {
  isDragOver.value = false
}
async function onAvatarDrop(event) {
  isDragOver.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    await uploadAvatar(file)
    showDragModal.value = false
  }
}

const onAvatarChange = async (event) => {
  const file = event.target.files[0]
  if (file) {
    await uploadAvatar(file)
    showDragModal.value = false
  }
}

async function uploadAvatar(file) {
  const formData = new FormData()
  formData.append('student_id', userId)
  formData.append('avatar', file)
  const res = await axios.post('http://localhost:5000/api/student/upload_avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  if (res.data.success) {
    setAvatarUrl()
  }
}

// 选课相关
const searchCourseId = ref('')
const searchCourseName = ref('')
const courses = ref([])
const courseMsg = ref('')
const onlyShowSelected = ref(false)

// 叠课相关变量
const showConflictDialog = ref(false)
const conflictCourseId = ref('')
const showOverlapDialog = ref(false)
const overlapApplications = ref([])
const selectedCourseTimes = ref([])

// 获取学生信息
const fetchStudentInfo = async () => {
  try {
    if (!userId) {
      passwordMsg.value = '未登录'
      return
    }
    const res = await axios.get('http://localhost:5000/api/student/info', {
      params: { id: userId }
    })
    if (res.data.success) {
      student.value = {
        id: res.data.id,
        name: res.data.name,
        gender: res.data.gender,
        birthday: res.data.birthday,
        contact: res.data.contact,
        major: res.data.major,
        class_id: res.data.class_id
      }
      editGender.value = res.data.gender || ''
      editBirthday.value = res.data.birthday ? res.data.birthday.slice(0, 10) : ''
      editContact.value = res.data.contact || ''
      editMajor.value = res.data.major || ''
    }
  } catch (e) {
    passwordMsg.value = '获取账号信息失败'
  }
}

// 保存学生信息
const saveStudentInfo = async () => {
  const res = await axios.post('http://localhost:5000/api/student/update_info', {
    student_id: student.value.id,
    gender: editGender.value,
    birthday: editBirthday.value || null,
    contact: editContact.value,
    major: editMajor.value
  })
  if (res.data.success) {
    infoMsg.value = '信息保存成功'
    fetchStudentInfo()
  } else {
    infoMsg.value = res.data.message || '保存失败'
  }
}

// 修改密码
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
      id: student.value.id,
      old_password: oldPassword.value,
      new_password: newPassword.value
    })
    if (res.data.success) {
      passwordMsg.value = '密码修改成功'
      oldPassword.value = ''
      newPassword.value = ''
    } else {
      passwordMsg.value = res.data.message || '密码修改失败'
    }
  } catch (e) {
    passwordMsg.value = '密码修改失败'
  }
}

// 解析课程时间字符串
function parseCourseTime(timeStr) {
  if (!timeStr) return [];
  let result = [];
  let parts = timeStr.split(':');
  let weekPart = '', dayPart = '';
  if (parts.length === 2) {
    weekPart = parts[0].replace('周', '');
    dayPart = parts[1];
  } else {
    dayPart = parts[0];
  }
  // 解析周数
  let weekList = [];
  if (weekPart) {
    weekPart.split(',').forEach(seg => {
      if (seg.includes('-')) {
        const [start, end] = seg.split('-').map(Number);
        for (let i = start; i <= end; i++) weekList.push(i);
      } else if (/^\d+$/.test(seg)) {
        weekList.push(Number(seg));
      }
    });
  }
  // 解析节次
  dayPart.split(';').forEach(seg => {
    seg = seg.trim();
    if (!seg) return;
    const m = seg.match(/^(\d+)\(([\d,]+)\)$/);
    if (!m) return;
    const day = Number(m[1]);
    const periods = m[2].split(',').map(Number);
    result.push({ day, periods, weeks: weekList });
  });
  return result;
}

// 检查时间冲突
function hasTimeConflict(newTimeStr, selectedTimesArr) {
  const newSlots = parseCourseTime(newTimeStr);
  for (const { time } of selectedTimesArr) {
    if (!time) continue;
    const slots = parseCourseTime(time);
    for (const slot1 of newSlots) {
      for (const slot2 of slots) {
        if (slot1.day === slot2.day) {
          if (slot1.periods.some(p => slot2.periods.includes(p))) {
            if (slot1.weeks.some(w => slot2.weeks.includes(w))) {
              return true;
            }
          }
        }
      }
    }
  }
  return false;
}

// 获取所有课程及选课状态（重写，保存selectedCourseTimes）
const fetchCourses = async () => {
  const params = {
    student_id: userId,
    course_id: searchCourseId.value,
    course_name: searchCourseName.value,
  }
  if (onlyShowSelected.value) params.only_selected = 1
  const res = await axios.get('http://localhost:5000/api/student/courses', { params })
  if (res.data.success) {
    courses.value = res.data.courses
    selectedCourseTimes.value = res.data.selected_course_times || []
  }
}

let fetchCoursesTimer = null
const fetchCoursesDebounced = () => {
  if (fetchCoursesTimer) clearTimeout(fetchCoursesTimer)
  fetchCoursesTimer = setTimeout(() => {
    fetchCourses()
  }, 400)
}

// 展示所有任课教师姓名
const getTeacherNames = (teachers) => {
  if (!teachers || !teachers.length) return ''
  return teachers.map(t => t.name).join('，')
}

// 选课（重写，冲突弹窗）
const selectCourse = async (course_id, item) => {
  const course = item || courses.value.find(c => c.course_id === course_id)
  if (course && course.numStudents >= course.maxStudents) {
    courseMsg.value = '人数已满，无法选课'
    setTimeout(() => { courseMsg.value = '' }, 1500)
    return
  }
  // 冲突检测
  if (course && hasTimeConflict(course.time, selectedCourseTimes.value)) {
    conflictCourseId.value = course.course_id
    showConflictDialog.value = true
    return
  }
  const res = await axios.post('http://localhost:5000/api/student/select_course', {
    student_id: userId,
    course_id
  })
  if (res.data.success) {
    courseMsg.value = '选课成功'
    fetchCourses()
    fetchTimetableData()
  } else {
    courseMsg.value = res.data.message || '选课失败'
  }
  setTimeout(() => { courseMsg.value = '' }, 1500)
}

// 叠课弹窗相关
const applyOverlap = async () => {
  showConflictDialog.value = false
  if (!conflictCourseId.value) return
  await axios.post('http://localhost:5000/api/student/apply_overlap', {
    student_id: userId,
    course_id: conflictCourseId.value
  })
  courseMsg.value = '已提交叠课申请'
  setTimeout(() => { courseMsg.value = '' }, 1500)
  conflictCourseId.value = ''
}

// 打开叠课申请列表
const openOverlapDialog = async () => {
  const res = await axios.get('http://localhost:5000/api/student/overlap_applications', {
    params: { student_id: userId }
  })
  if (res.data.success) overlapApplications.value = res.data.applications
  showOverlapDialog.value = true
}

// 撤销叠课申请
const cancelOverlap = async (course_id) => {
  await axios.post('http://localhost:5000/api/student/cancel_overlap', {
    student_id: userId,
    course_id
  })
  openOverlapDialog()
}

const statusText = (status) => ({
  pending: '待处理',
  approved: '已通过'
}[status] || '')

// 获取课程表相关
const timetableTable = ref([])
const timetableDays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const hoveredCard = ref(null)
const timetableSections = [
  { label: '上午', start: 0, end: 4 },
  { label: '下午', start: 5, end: 9 },
  { label: '晚上', start: 10, end: 12 }
]

const fetchTimetableData = async () => {
  try {
    const res = await axios.get('http://localhost:5000/api/student/timetable', {
      params: { student_id: userId }
    })
    if (res.data.success) {
      timetableTable.value = res.data.table
    }
  } catch (e) {
    console.error('获取课程表失败', e)
  }
}

function logout() {
  localStorage.removeItem('user_id')
  router.push('/')
}

// 退课确认弹窗相关
const showDropConfirm = ref(false)
const dropCourseId = ref('')

// 触发退课确认弹窗
const confirmDropCourse = (course_id) => {
  dropCourseId.value = course_id
  showDropConfirm.value = true
}

// 真正执行退课
const doDropCourse = async () => {
  showDropConfirm.value = false
  if (!dropCourseId.value) return
  const res = await axios.post('http://localhost:5000/api/student/drop_course', {
    student_id: userId,
    course_id: dropCourseId.value
  })
  if (res.data.success) {
    courseMsg.value = '退课成功'
    fetchCourses()
    fetchTimetableData()
  } else {
    courseMsg.value = res.data.message || '退课失败'
  }
  setTimeout(() => { courseMsg.value = '' }, 1500)
  dropCourseId.value = ''
}

onMounted(() => {
  fetchStudentInfo()
  fetchCourses()
  fetchTimetableData()
  setAvatarUrl()
})
</script>

<style scoped>
/* 复用 TeacherDashboard.vue 的样式 */
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
.avatar-row {
  display: flex;
  align-items: center;
  gap: 32px;
  margin-left: 80px;
  margin-bottom: 32px;
  margin-top: 24px;
}
.avatar-img {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #5dade2;
  box-shadow: 0 4px 16px rgba(44,62,80,0.18);
  background: #fff;
  transition: box-shadow 0.2s;
}
.avatar-img:hover {
  box-shadow: 0 8px 32px #5dade2;
}
.avatar-upload-btn {
  background: linear-gradient(90deg, #5dade2 0%, #90caf9 100%);
  color: #232526;
  border: none;
  border-radius: 6px;
  padding: 10px 28px;
  font-size: 18px;
  cursor: pointer;
  font-weight: bold;
  box-shadow: 0 2px 8px #2c3e50;
  transition: background 0.2s;
  display: inline-block;
}
.avatar-upload-btn:hover {
  background: linear-gradient(90deg, #90caf9 0%, #5dade2 100%);
  color: #232526;
}
.avatar-input {
  display: none;
}

/* 拖拽弹窗样式 */
.avatar-drag-modal {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(44,62,80,0.25);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}
.avatar-drag-window {
  background: #fff;
  border-radius: 14px;
  padding: 36px 40px 28px 40px;
  box-shadow: 0 8px 32px rgba(44,62,80,0.18);
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 2px dashed #5dade2;
  min-width: 320px;
  min-height: 220px;
  position: relative;
  transition: background 0.2s, border-color 0.2s;
}
.avatar-dragover {
  background: #e3f2fd;
  border-color: #1976d2;
}
.avatar-drag-title {
  font-size: 18px;
  color: #1976d2;
  margin-bottom: 18px;
  font-weight: bold;
}
.avatar-drag-tip {
  color: #5dade2;
  font-size: 14px;
  margin-top: 12px;
  opacity: 0.8;
}
.avatar-cancel-btn {
  position: absolute;
  right: 18px;
  top: 14px;
  background: none;
  border: none;
  color: #888;
  font-size: 16px;
  cursor: pointer;
  font-weight: bold;
  transition: color 0.2s;
}
.avatar-cancel-btn:hover {
  color: #1976d2;
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
.form-row input[type="date"] {
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
.form-row select {
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
.form-row button:hover {
  background: linear-gradient(90deg, #90caf9 0%, #5dade2 100%);
  color: #232526;
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
.password-msg {
  margin-top: 8px;
  color: #5dade2;
  font-size: 16px;
  text-align: center;
}
.account-manage-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  background: rgba(44, 62, 80, 0.92);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  margin-bottom: 24px;
}
.search-input {
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
.add-account-panel {
  width: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.account-list {
  width: 100%;
  flex: 1;
  background: rgba(44, 62, 80, 0.85);
  border-radius: 12px;
  padding: 12px 0;
  min-height: 240px;
  overflow-y: auto;
}
.account-item,
.account-item.header-row {
  display: grid;
  grid-template-columns: 120px 1fr 100px 120px 150px 1fr 150px auto;
  align-items: center;
  padding: 14px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}
.account-role,
.cell-wrap {
  white-space: pre-wrap;
  word-break: break-all;
  max-width: 180px;      
  max-height: 48px;      
  overflow-y: auto;
  display: block;
}
.account-item.header-row {
  background: rgba(86, 174, 255, 0.1);
  font-weight: bold;
  color: #5dade2;
}
.account-action {
  text-align: right;
}
.add-btn, .del-btn {
  background: linear-gradient(90deg, #5dade2 0%, #90caf9 100%);
  color: #232526;
  border: none;
  border-radius: 6px;
  padding: 0 16px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
  font-weight: bold;
  height: 36px;
  line-height: 36px;
  white-space: nowrap;
  display: inline-block;
}
.add-btn:hover, .del-btn:hover {
  background: linear-gradient(90deg, #90caf9 0%, #5dade2 100%);
  color: #232526;
}
.del-btn {
  background: #ff7675;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 0 16px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
  font-weight: bold;
  height: 36px;
  line-height: 36px;
  white-space: nowrap;
  display: inline-block;
}
.del-btn:hover {
  background: #ff5252;
  color: #fff;
}
.empty-tip {
  grid-column: 1 / -1;
  text-align: center;
  padding: 18px 0;
  color: #5dade2;
  font-size: 18px;
}
.dialog-msg {
  margin-top: 12px;
  color: #5dade2;
  font-size: 16px;
  text-align: center;
}

/* 课程表样式 */
.timetable-panel {
  padding: 40px 0;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  min-height: 80vh;
}
.timetable {
  width: 1000px;
  max-width: 98vw;
  border-collapse: collapse;
  background: rgba(255,255,255,0.06);
  font-size: 18px;
  box-shadow: 0 4px 24px rgba(44,62,80,0.15);
  border-radius: 12px;
  overflow: hidden;
  table-layout: fixed;
}
.timetable th,
.timetable td {
  width: 120px;
  height: 70px;
  max-width: 120px;
  max-height: 70px;
  overflow: hidden;
  position: relative;
  padding: 0;
  vertical-align: top;
}
.timetable-cell {
  position: relative;
  padding: 2px 2px;
  overflow: hidden;
  height: 70px;
}
.course-card {
  background: #e3eafc;
  border-radius: 8px;
  margin: 2px 0;
  padding: 4px 6px;
  box-shadow: 0 2px 8px #5dade222;
  font-size: 14px;
  color: #232526;
  line-height: 1.4;
  transition: height 0.2s, z-index 0.2s, box-shadow 0.2s;
  overflow: hidden;
  position: relative;
  cursor: pointer;
  height: auto;
  z-index: 1;
  max-height: 60px;
  white-space: normal;
}
.course-card.compressed {
  height: 28px;
  max-height: 28px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  font-size: 13px;
  z-index: 1;
}
.course-card.expanded {
  height: auto;
  max-height: 200px;
  background: #fff;
  box-shadow: 0 4px 16px #5dade244;
  z-index: 10;
}
.course-name {
  font-weight: bold;
  color: #1976d2;
  font-size: 15px;
}
.course-weeks {
  color: #666;
  font-size: 12px;
  margin-top: 2px;
}
.course-location {
  color: #1976d2;
  font-size: 12px;
  margin-top: 2px;
}
.timetable-section {
  background: transparent; /* 统一背景 */
  color: #5dade2;
  font-weight: bold;
  text-align: center;
  font-size: 16px;
  border-right: 1px solid #e0e0e0;
  min-width: 48px;
  /* 分割线样式由下方选择器控制 */
}

/* 分割线：下午、晚上前加粗线 */
.timetable-section + .timetable-section {
  border-top: 3px solid #5dade2;
}
tr.section-divider td {
  border-top: 3px solid #5dade2 !important;
  padding: 0;
  height: 0;
  background: transparent;
}
.overlap-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  color: #555;
  font-size: 16px;
}
.small-btn {
  padding: 4px 14px;
  font-size: 14px;
  border-radius: 4px;
  background: #ff7675;
  color: #fff;
  border: none;
  cursor: pointer;
  margin-left: 18px;
  transition: background 0.2s;
}
.small-btn:hover {
  background: #ff5252;
}
.conflict-dialog-mask, .dialog-mask {
  position: fixed;
  left: 0; top: 0; right: 0; bottom: 0;
  background: rgba(44,62,80,0.25);
  z-index: 3000;
  display: flex; align-items: center; justify-content: center;
}
.conflict-dialog, .dialog {
  background: #fff;
  border-radius: 12px;
  padding: 32px 40px 24px 40px;
  box-shadow: 0 8px 32px rgba(44,62,80,0.18);
  min-width: 320px;
  min-height: 120px;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.conflict-title {
  font-size: 22px;
  color: #e74c3c;
  font-weight: bold;
  margin-bottom: 18px;
}
.conflict-msg {
  color: #232526;
  font-size: 17px;
  margin-bottom: 24px;
}
.conflict-actions {
  display: flex;
  gap: 24px;
}
.conflict-btn {
  background: #e0e0e0;
  color: #232526;
  border: none;
  border-radius: 6px;
  padding: 8px 28px;
  font-size: 16px;
  cursor: pointer;
  font-weight: bold;
  transition: background 0.2s;
}
.conflict-btn:hover {
  background: #5dade2;
  color: #fff;
}
</style>