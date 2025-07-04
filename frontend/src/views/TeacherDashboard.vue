<template>
  <div class="admin-dashboard">
    <aside class="sidebar">
      <div class="logo">教务系统</div>
      <ul>
        <li :class="{active: activeMenu==='account'}" @click="activeMenu='account'">账号信息</li>
        <li :class="{active: activeMenu==='course'}" @click="activeMenu='course'">教师授课</li>
        <li :class="{active: activeMenu==='headteacher'}" @click="activeMenu='headteacher'">班主任管理</li>
        <li @click="logout" class="logout">退出登录</li>
      </ul>
    </aside>
    <main class="main-content">
      <transition name="fade" mode="out-in">
        <!-- 账号信息 -->
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
          <form class="account-form" @submit.prevent="saveTeacherInfo">
            <div class="form-row">
              <label>教师工号：</label>
              <input type="text" :value="teacher.id" readonly />
            </div>
            <div class="form-row">
              <label>姓名：</label>
              <input type="text" :value="teacher.name" readonly />
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
              <label>职称：</label>
              <input type="text" v-model="editTitle" placeholder="请输入职称" />
            </div>
            <div class="form-row">
              <label>联系方式：</label>
              <input type="text" v-model="editContact" placeholder="请输入联系方式" />
            </div>
            <div class="form-row">
              <button type="submit">保存信息</button>
            </div>
            <div v-if="infoMsg" class="password-msg">{{ infoMsg }}</div>
          </form>
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
        <!-- 教师任课 -->
        <div v-else-if="activeMenu==='course'" key="course" class="add-account-panel">
          <div class="account-manage-header">
            <input v-model="courseSearchKeyword" @input="fetchCourses" placeholder="搜索课程..." class="search-input" />
            <button class="add-btn" @click="showAddCourseDialog = true">添加任课</button>
            <!-- 叠课申请处理按钮（放在教师授课页面搜索栏旁或合适位置） -->
            <button @click="openOverlapDialog" style="margin-left:16px;">叠课申请处理</button>
          </div>
          <!-- 叠课申请处理弹窗 -->
          <div v-if="showOverlapDialog" class="dialog-mask">
            <div class="dialog">
              <h3>叠课申请处理</h3>
              <div v-for="app in overlapApplications" :key="app.student_id + '-' + app.course_id" class="overlap-row">
                <span>
                  学生：{{ app.student_name }} | 课程：{{ app.course_name }}
                </span>
                <span>
                  <button class="small-btn" @click="processOverlap(app.student_id, app.course_id, 'approve')">同意</button>
                  <button class="small-btn" @click="processOverlap(app.student_id, app.course_id, 'reject')">拒绝</button>
                </span>
              </div>
              <button @click="showOverlapDialog = false">关闭</button>
            </div>
          </div>
          <div class="account-list">
            <!-- 表头 -->
            <div class="account-item header-row">
              <span class="account-id">课程号</span>
              <span class="account-role">课程名</span>
              <span class="account-role">学分</span>
              <span class="account-role">上课地点</span>
              <span class="account-role">上课时间</span>
              <span class="account-role">任课教师</span>
              <span class="account-role">选课人数/上限</span> <!-- 新增 -->
              <span class="account-action"></span>
            </div>
            <!-- 数据行 -->
            <div v-for="item in courses" :key="item.teacher_course_id" class="account-item">
              <span class="account-id">{{ item.course_id }}</span>
              <span class="account-role">{{ item.name }}</span>
              <span class="account-role">{{ item.credit }}</span>
              <span class="account-role">{{ item.location }}</span>
              <span class="account-role cell-wrap">{{ item.time }}</span>
              <span class="account-role">{{ getTeacherNames(item.teachers) }}</span>
              <span class="account-role">{{ item.numStudents }} / {{ item.maxStudents }}</span> <!-- 新增 -->
              <span class="account-action">
                <button class="edit-btn" @click="openEditCourse(item)">修改</button>
                <button
                  class="del-btn"
                  v-if="item.teachers.includes(teacher.id)"
                  @click="openDeleteCourse(item)"
                >删除课程</button>
              </span>
            </div>
            <div v-if="courses.length === 0" class="empty-tip">暂无课程</div>
          </div>
          <!-- 添加任课弹窗 -->
          <div v-if="showAddCourseDialog" class="dialog-mask">
            <div class="dialog">
              <h3>添加课程</h3>
              <div>
                <label>课程号：</label>
                <input v-model="addCourseId" placeholder="请输入课程号" />
              </div>
              <div>
                <label>课程名：</label>
                <input v-model="addCourseName" placeholder="请输入课程名" />
              </div>
              <div>
                <label>学分：</label>
                <input v-model="addCourseCredit" placeholder="请输入学分" />
              </div>
              <div>
                <label>上课地点：</label>
                <input v-model="addCourseLocation" placeholder="请输入上课地点" />
              </div>
              <div>
                <label>上课周数：</label>
                <div style="display:flex;flex-wrap:wrap;gap:8px;max-height:90px;overflow:auto;">
                  <label v-for="w in 18" :key="w" style="width:60px;">
                    <input type="checkbox" :value="w" v-model="selectedWeeks" /> 第{{w}}周
                  </label>
                </div>
              </div>
              <div>
                <label>上课时间（可添加多组）：</label>
                <div v-for="(item, idx) in timeGroups" :key="idx" style="margin-bottom:8px;">
                  <select v-model="item.day" style="width:90px;">
                    <option v-for="d in 7" :key="d" :value="d">星期{{'日一二三四五六'[d%7]}}</option>
                  </select>
                  <span style="margin:0 8px;">节次：</span>
                  <span v-for="n in 13" :key="n">
                    <input type="checkbox" :value="n" v-model="item.sections" />{{n}}
                  </span>
                  <button @click="removeTimeGroup(idx)" style="margin-left:8px;color:#ff7675;">移除</button>
                </div>
                <button @click="addTimeGroup" style="margin-top:6px;">添加一组上课时间</button>
              </div>
              <div>
                <label>任课教师：</label>
                <div v-for="(tid, idx) in addCourseTeachers" :key="idx" style="display:flex;align-items:center;margin-bottom:8px;">
                  <select v-model="addCourseTeachers[idx]" :disabled="tid === userId">
                    <option
                      v-for="t in allTeachers"
                      :key="t.teacher_id"
                      :value="t.teacher_id"
                      :disabled="addCourseTeachers.includes(t.teacher_id) && addCourseTeachers[idx] !== t.teacher_id"
                    >
                      {{ t.teacher_id }} - {{ t.name }}
                    </option>
                  </select>
                  <button
                    v-if="tid !== userId"
                    @click="removeTeacherGroup(idx)"
                    style="margin-left:8px;color:#ff7675;"
                  >移除</button>
                  <span v-else style="margin-left:8px;color:#90caf9;">(本人)</span>
                </div>
                <button @click="addTeacherGroup" style="margin-top:6px;">添加一位教师</button>
              </div>
              <div>
                <label>选课人数上限：</label>
                <input v-model="addCourseMaxStudents" type="number" min="1" placeholder="请输入上限人数" />
              </div>
              <div class="dialog-actions">
                <button @click="createAndAddCourse">确认</button>
                <button @click="showAddCourseDialog = false">取消</button>
              </div>
              <div v-if="addCourseMsg" class="dialog-msg">{{ addCourseMsg }}</div>
            </div>
          </div>
          <!-- 修改任课弹窗 -->
          <div v-if="showEditCourseDialog" class="dialog-mask">
            <div class="dialog">
              <h3>修改课程信息</h3>
              <div>
                <label>课程号：</label>
                <input v-model="editCourseId" disabled />
              </div>
              <div>
                <label>课程名：</label>
                <input v-model="editCourseName" />
              </div>
              <div>
                <label>学分：</label>
                <input v-model="editCourseCredit" />
              </div>
              <div>
                <label>上课地点：</label>
                <input v-model="editCourseLocation" />
              </div>
              <div>
                <label>上课周数：</label>
                <div style="display:flex;flex-wrap:wrap;gap:8px;max-height:90px;overflow:auto;">
                  <label v-for="w in 18" :key="w" style="width:60px;">
                    <input type="checkbox" :value="w" v-model="editSelectedWeeks" /> 第{{w}}周
                  </label>
                </div>
              </div>
              <div>
                <label>上课时间（可添加多组）：</label>
                <div v-for="(item, idx) in editTimeGroups" :key="idx" style="margin-bottom:8px;">
                  <select v-model="item.day" style="width:90px;">
                    <option v-for="d in 7" :key="d" :value="d">星期{{'日一二三四五六'[d%7]}}</option>
                  </select>
                  <span style="margin:0 8px;">节次：</span>
                  <span v-for="n in 13" :key="n">
                    <input type="checkbox" :value="n" v-model="item.sections" />{{n}}
                  </span>
                  <button @click="removeEditTimeGroup(idx)" style="margin-left:8px;color:#ff7675;">移除</button>
                </div>
                <button @click="addEditTimeGroup" style="margin-top:6px;">添加一组上课时间</button>
              </div>
              <div>
                <label>任课教师：</label>
                <div v-for="(tid, idx) in editCourseTeachers" :key="idx" style="display:flex;align-items:center;margin-bottom:8px;">
                  <select v-model="editCourseTeachers[idx]" :disabled="tid === userId">
                    <option
                      v-for="t in allTeachers"
                      :key="t.teacher_id"
                      :value="t.teacher_id"
                      :disabled="editCourseTeachers.includes(t.teacher_id) && editCourseTeachers[idx] !== t.teacher_id"
                    >
                      {{ t.teacher_id }} - {{ t.name }}
                    </option>
                  </select>
                  <button
                    v-if="tid !== userId"
                    @click="removeEditTeacherGroup(idx)"
                    style="margin-left:8px;color:#ff7675;"
                  >移除</button>
                  <span v-else style="margin-left:8px;color:#90caf9;">(本人)</span>
                </div>
                <button @click="addEditTeacherGroup" style="margin-top:6px;">添加一位教师</button>
              </div>
              <!-- 这里是选课人数上限输入框，确保它在弹窗中 -->
              <div>
                <label>选课人数上限：</label>
                <input v-model="editCourseMaxStudents" type="number" min="1" placeholder="请输入上限人数" />
              </div>
              <div class="dialog-actions">
                <button @click="saveEditCourse">保存</button>
                <button @click="showEditCourseDialog = false">取消</button>
              </div>
              <div v-if="editCourseMsg" class="dialog-msg">{{ editCourseMsg }}</div>
            </div>
          </div>
          <!-- 删除任课弹窗 -->
          <div v-if="showDelCourseDialog" class="dialog-mask">
            <div class="dialog">
              <h3>确认删除</h3>
              <div>确定要删除该任课记录吗？</div>
              <div class="dialog-actions">
                <button @click="deleteCourse">确认</button>
                <button @click="showDelCourseDialog = false">取消</button>
              </div>
              <div v-if="delCourseMsg" class="dialog-msg">{{ delCourseMsg }}</div>
            </div>
          </div>
        </div>
        <!-- 班主任管理 -->
        <div v-else-if="activeMenu==='headteacher'" key="headteacher" class="add-account-panel">
          <div class="account-manage-header" style="align-items: flex-start;">
            <div style="flex:1;">
              <div v-if="currentHeadClass" class="account-item" style="background:rgba(93,173,226,0.10);margin-bottom:10px;">
                <span class="account-id">班级号：{{ currentHeadClass.class_id }}</span>
                <span class="account-role">班级名：{{ currentHeadClass.name }}</span>
                <span class="account-role">所属学院：{{ getCollegeName(currentHeadClass.college_id) }}</span>
                <button class="edit-btn" @click="showChangeHeadClassDialog = true" style="margin-left:24px;">更改</button>
              </div>
              <div v-else class="account-item" style="background:rgba(93,173,226,0.10);margin-bottom:10px;">
                <span style="color:#ff7675;">当前没有担任班主任</span>
                <button class="edit-btn" @click="showChangeHeadClassDialog = true" style="margin-left:24px;">选择班级</button>
              </div>
            </div>
          </div>
          <!-- 更换/取消班主任弹窗 -->
          <div v-if="showChangeHeadClassDialog" class="dialog-mask">
            <div class="dialog">
              <h3>更换/取消班主任</h3>
              <div>
                <label>选择班级：</label>
                <select v-model="changeHeadClassId">
                  <option value="">取消班主任</option>
                  <option v-for="clazz in allClasses" :key="clazz.class_id" :value="clazz.class_id">
                    {{ clazz.class_id }} - {{ clazz.name }}
                  </option>
                </select>
              </div>
              <div class="dialog-actions">
                <button @click="changeHeadClass">确认</button>
                <button @click="showChangeHeadClassDialog = false">取消</button>
              </div>
              <div v-if="changeHeadClassMsg" class="dialog-msg">{{ changeHeadClassMsg }}</div>
            </div>
          </div>
          <!-- 搜索框和添加学生按钮 -->
          <div class="account-manage-header" style="margin-top:10px;">
            <input v-model="studentSearchKeyword" @input="fetchClassStudents" placeholder="搜索学生..." class="search-input" />
            <button class="add-btn" @click="showAddStudentDialog = true" :disabled="!currentHeadClass">添加学生</button>
          </div>
          <div class="account-list">
            <!-- 表头 -->
            <div class="account-item" style="font-weight:bold;background:rgba(93,173,226,0.10);">
              <span class="account-id">学号</span>
              <span class="account-role">姓名</span>
              <span class="account-role">性别</span>
              <span class="account-role">生日</span>
              <span class="account-role">联系方式</span>
              <span class="account-role">专业</span>
              <span style="width:120px"></span>
            </div>
            <!-- 数据行 -->
            <div v-for="item in classStudents" :key="item.student_id" class="account-item">
              <span class="account-id">{{ item.student_id }}</span>
              <span class="account-role">{{ item.name }}</span>
              <span class="account-role">{{ item.gender }}</span>
              <span class="account-role">{{ item.birthday ? item.birthday.slice(0,10) : '' }}</span>
              <span class="account-role">{{ item.contact }}</span>
              <span class="account-role">{{ item.major }}</span>
              <button class="del-btn" @click="openRemoveStudent(item)">移出班级</button>
            </div>
            <div v-if="classStudents.length === 0" class="empty-tip">暂无学生</div>
          </div>
          <!-- 添加学生弹窗 -->
          <div v-if="showAddStudentDialog" class="dialog-mask">
            <div class="dialog">
              <h3>添加学生</h3>
              <div>
                <label>搜索学生：</label>
                <input v-model="unassignedSearchKeyword" @keyup.enter="fetchUnassignedStudents" placeholder="输入学号或姓名" />
                <button @click="fetchUnassignedStudents">搜索</button>
              </div>
              <div style="max-height:200px;overflow:auto;margin-top:10px;">
                <div v-for="stu in unassignedStudents" :key="stu.student_id"
                     :class="['student-select-item', {selected: addStudentId === stu.student_id}]"
                     @click="addStudentId = stu.student_id"
                     style="padding:8px 0;cursor:pointer;">
                  <span>{{ stu.student_id }} - {{ stu.name }}，{{ stu.gender || '未知' }}，{{ stu.major || '无专业' }}</span>
                  <span v-if="addStudentId === stu.student_id" style="color:#5dade2;margin-left:10px;">✔</span>
                </div>
                <div v-if="unassignedStudents.length === 0" style="color:#90caf9;text-align:center;padding: 12px 0;">无匹配学生</div>
              </div>
              <div class="dialog-actions">
                <button @click="addStudent">确认</button>
                <button @click="showAddStudentDialog = false">取消</button>
              </div>
              <div v-if="addStudentMsg" class="dialog-msg">{{ addStudentMsg }}</div>
            </div>
          </div>
          <!-- 移除学生弹窗 -->
          <div v-if="showRemoveStudentDialog" class="dialog-mask">
            <div class="dialog">
              <h3>确认移出</h3>
              <div>确定要将学生 <b>{{ removeStudentId }}</b> 移出班级吗？</div>
              <div class="dialog-actions">
                <button @click="removeStudent">确认</button>
                <button @click="showRemoveStudentDialog.value = false">取消</button>
              </div>
              <div v-if="removeStudentMsg" class="dialog-msg">{{ removeStudentMsg }}</div>
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
const userId = localStorage.getItem('user_id')
const addCourseTeachers = ref([userId]) // 默认本人

// 账号信息相关
const teacher = ref({ id: '', name: '', gender: '', birthday: '', title: '', contact: '' })
const oldPassword = ref('')
const newPassword = ref('')
const passwordMsg = ref('')
const editGender = ref('')
const editBirthday = ref('')
const editTitle = ref('')
const editContact = ref('')
const infoMsg = ref('')

const fetchTeacherInfo = async () => {
  try {
    const userId = localStorage.getItem('user_id')
    if (!userId) {
      passwordMsg.value = '未登录'
      return
    }
    const res = await axios.get('http://localhost:5000/api/teacher/info', {
      params: { id: userId }
    })
    if (res.data.success) {
      teacher.value = {
        id: res.data.id,
        name: res.data.name,
        gender: res.data.gender,
        birthday: res.data.birthday,
        title: res.data.title,
        contact: res.data.contact
      }
      editGender.value = res.data.gender || ''
      editBirthday.value = res.data.birthday ? res.data.birthday.slice(0, 10) : ''
      editTitle.value = res.data.title || ''
      editContact.value = res.data.contact || ''
    }
  } catch (e) {
    passwordMsg.value = '获取账号信息失败'
  }
}

const saveTeacherInfo = async () => {
  const userId = teacher.value.id
  const res = await axios.post('http://localhost:5000/api/teacher/update_info', {
    teacher_id: userId,
    gender: editGender.value,
    birthday: editBirthday.value || null,
    title: editTitle.value,
    contact: editContact.value
  })
  if (res.data.success) {
    infoMsg.value = '信息保存成功'
    fetchTeacherInfo()
  } else {
    infoMsg.value = res.data.message || '保存失败'
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
      id: teacher.value.id,
      old_password: oldPassword.value,
      new_password: newPassword.value
    })
    if (res.data.success) {
      passwordMsg.value = '密码修改成功'
      teacher.value.password = res.data.password
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

// 班主任相关
const currentHeadClass = ref(null)
const showChangeHeadClassDialog = ref(false)
const changeHeadClassId = ref('')
const changeHeadClassMsg = ref('')
const allClasses = ref([])
const colleges = ref([])

const fetchCurrentHeadClass = async () => {
  const userId = localStorage.getItem('user_id')
  if (!userId) return
  const res = await axios.get('http://localhost:5000/api/teacher/current_head_class', {
    params: { teacher_id: userId }
  })
  currentHeadClass.value = res.data.class || null
  // 默认选中当前班级
  changeHeadClassId.value = currentHeadClass.value ? currentHeadClass.value.class_id : ''
}
const fetchAllClasses = async () => {
  const res = await axios.get('http://localhost:5000/api/admin/classes')
  allClasses.value = res.data.classes || []
}
const fetchColleges = async () => {
  const res = await axios.get('http://localhost:5000/api/teacher/admin/colleges')
  if (res.data.success) colleges.value = res.data.colleges
}
const changeHeadClass = async () => {
  const userId = localStorage.getItem('user_id')
  if (!userId) return
  const res = await axios.post('http://localhost:5000/api/teacher/change_head_class', {
    teacher_id: userId,
    class_id: changeHeadClassId.value
  })
  if (res.data.success) {
    changeHeadClassMsg.value = '班主任班级更换成功'
    // 重新获取当前班主任班级
    await fetchCurrentHeadClass()
    showChangeHeadClassDialog.value = false
  } else {
    changeHeadClassMsg.value = res.data.message || '更换失败'
  }
}

const getCollegeName = (college_id) => {
  const college = colleges.value.find(c => c.college_id === college_id)
  return college ? college.name : college_id
}

// 班级学生相关
const studentSearchKeyword = ref('')
const classStudents = ref([])
const fetchClassStudents = async () => {
  if (!currentHeadClass.value) {
    classStudents.value = []
    return
  }
  const res = await axios.get('http://localhost:5000/api/teacher/class_students', {
    params: { class_id: currentHeadClass.value.class_id, keyword: studentSearchKeyword.value }
  })
  classStudents.value = res.data.students || []
}

// 添加学生
const showAddStudentDialog = ref(false)
const addStudentId = ref('')
const addStudentMsg = ref('')
const unassignedStudents = ref([])
const unassignedSearchKeyword = ref('')

// 获取未分班学生
const fetchUnassignedStudents = async () => {
  const res = await axios.get('http://localhost:5000/api/teacher/unassigned_students', {
    params: { keyword: unassignedSearchKeyword.value }
  })
  if (res.data.success) unassignedStudents.value = res.data.students
}

// 每次打开弹窗时自动刷新
watch(showAddStudentDialog, (val) => {
  if (val) {
    unassignedSearchKeyword.value = ''
    fetchUnassignedStudents()
  }
})

const addStudent = async () => {
  if (!addStudentId.value) {
    addStudentMsg.value = '请选择学生'
    return
  }
  const res = await axios.post('http://localhost:5000/api/teacher/add_student', {
    class_id: currentHeadClass.value.class_id,
    student_id: addStudentId.value
  })
  if (res.data.success) {
    addStudentMsg.value = '学生添加成功'
    addStudentId.value = ''
    fetchClassStudents()
    fetchUnassignedStudents()
    setTimeout(() => { showAddStudentDialog.value = false }, 800)
  } else {
    addStudentMsg.value = res.data.message || '添加失败'
  }
}

// 打开弹窗时刷新未分班学生
watch(showAddStudentDialog, (val) => {
  if (val) fetchUnassignedStudents()
})

const showRemoveStudentDialog = ref(false)
const removeStudentId = ref('')
const removeStudentMsg = ref('')

const openRemoveStudent = (item) => {
  removeStudentId.value = item.student_id
  removeStudentMsg.value = ''
  showRemoveStudentDialog.value = true
}

const removeStudent = async () => {
  const res = await axios.post('http://localhost:5000/api/teacher/remove_student', {
    student_id: removeStudentId.value
  })
  if (res.data.success) {
    removeStudentMsg.value = '移除成功'
    fetchClassStudents()
    fetchUnassignedStudents()
    setTimeout(() => { showRemoveStudentDialog.value = false }, 800)
  } else {
    removeStudentMsg.value = res.data.message || '移除失败'
  }
}

// 教师任课相关
const courseSearchKeyword = ref('')
const courses = ref([])

const allCourses = ref([])
const allTeachers = ref([])

const showAddCourseDialog = ref(false)
const showEditCourseDialog = ref(false)

const addCourseId = ref('')
const addCourseName = ref('')
const addCourseCredit = ref('')
const addCourseLocation = ref('')
const addCourseMsg = ref('')
const addCourseMaxStudents = ref('') // 新增：选课人数上限

// 修改课程相关变量
const editCourseId = ref('')
const editCourseName = ref('')
const editCourseCredit = ref('')
const editCourseLocation = ref('')
const editSelectedWeeks = ref([])
const editTimeGroups = ref([{ day: 1, sections: [] }])
const editCourseTeachers = ref([userId])
const editCourseMsg = ref('')
const editCourseMaxStudents = ref('')

const deleteCourseMsg = ref('')
const showDelCourseDialog = ref(false)
const deleteCourseId = ref('')
const deleteCourseName = ref('')

// 头像相关
const defaultAvatar = '/assets/default_avatar.png'
const avatarUrl = ref('')
function setAvatarUrl() {
  avatarUrl.value = `/assets/${userId}/avatar.png?${Date.now()}`
}
function onAvatarError() {
  avatarUrl.value = defaultAvatar
}
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
  formData.append('teacher_id', userId)
  formData.append('avatar', file)
  const res = await axios.post('http://localhost:5000/api/teacher/upload_avatar', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
  if (res.data.success) {
    setAvatarUrl()
  }
}

// 获取课程列表（带搜索）
const fetchCourses = async () => {
  const userId = localStorage.getItem('user_id')
  const res = await axios.get('http://localhost:5000/api/teacher/teacher_courses', {
    params: { teacher_id: userId, keyword: courseSearchKeyword.value }
  })
  if (res.data.success) courses.value = res.data.courses
}

// 获取所有课程和教师（用于下拉）
const fetchAllCourses = async () => {
  const res = await axios.get('http://localhost:5000/api/teacher/admin/courses')
  if (res.data.success) allCourses.value = res.data.courses
}
const fetchAllTeachers = async () => {
  const res = await axios.get('http://localhost:5000/api/teacher/admin/teachers')
  if (res.data.success) allTeachers.value = res.data.teachers
}

// 获取教师姓名（支持多教师）
const getTeacherNames = (teacherIds) => {
  if (!teacherIds) return ''
  return teacherIds.map(id => {
    const t = allTeachers.value.find(x => x.teacher_id === id)
    return t ? t.name : id
  }).join('，')
}

// 修改课程弹窗
const openEditCourse = (item) => {
  editCourseId.value = item.course_id
  editCourseName.value = item.name
  editCourseCredit.value = item.credit
  editCourseLocation.value = item.location
  editCourseMaxStudents.value = item.maxStudents || ''
  // 解析时间
  const parsed = parseCourseTime(item.time)
  editSelectedWeeks.value = parsed.weeks
  editTimeGroups.value = parsed.groups
  // 解析教师
  editCourseTeachers.value = item.teachers && item.teachers.length
    ? [...item.teachers]
    : [userId]
  // 确保本人在列表且不可移除
  if (!editCourseTeachers.value.includes(userId)) {
    editCourseTeachers.value.unshift(userId)
  }
  editCourseMsg.value = ''
  showEditCourseDialog.value = true
}

// 解析 time 字符串为组件数据
function parseCourseTime(timeStr) {
  // 例：1,2,3,4,5周:1(1,2);3(3,4)
  if (!timeStr) return { weeks: [], groups: [{ day: 1, sections: [] }] }
  const [weeksPart, timesPart] = timeStr.split('周:')
  const weeks = weeksPart ? weeksPart.split(',').map(Number) : []
  const groups = []
  if (timesPart) {
    timesPart.split(';').forEach(seg => {
      const match = seg.match(/^(\d)\(([\d,]+)\)$/)
      if (match) {
        groups.push({
          day: Number(match[1]),
          sections: match[2].split(',').map(Number)
        })
      }
    })
  }
  return { weeks, groups: groups.length ? groups : [{ day: 1, sections: [] }] }
}

// 构建 time 字符串
function buildEditCourseTime() {
  if (!editSelectedWeeks.value.length || !editTimeGroups.value.length) return ''
  const weeks = editSelectedWeeks.value.sort((a, b) => a - b).join(',')
  const timeStr = editTimeGroups.value
    .filter(g => g.sections.length)
    .map(g => `${g.day}(${g.sections.sort((a, b) => a - b).join(',')})`)
    .join(';')
  if (!timeStr) return ''
  return `${weeks}周:${timeStr}`
}

// 添加/移除时间组
function addEditTimeGroup() {
  editTimeGroups.value.push({ day: 1, sections: [] })
}
function removeEditTimeGroup(idx) {
  editTimeGroups.value.splice(idx, 1)
}

// 添加/移除教师
function addEditTeacherGroup() {
  editCourseTeachers.value.push('')
}
function removeEditTeacherGroup(idx) {
  if (editCourseTeachers.value[idx] !== userId) {
    editCourseTeachers.value.splice(idx, 1)
  }
}

// 保存修改
async function saveEditCourse() {
  if (
    !editCourseName.value ||
    !editCourseCredit.value ||
    !editCourseLocation.value ||
    !editSelectedWeeks.value.length ||
    !editTimeGroups.value.some(g => g.sections.length) ||
    !editCourseTeachers.value.length
  ) {
    editCourseMsg.value = '请填写完整课程信息'
    return
  }
  const teachers = editCourseTeachers.value.filter(Boolean)
  const uniqueTeachers = [...new Set(teachers)]
  if (!uniqueTeachers.includes(userId)) uniqueTeachers.push(userId)
  if (uniqueTeachers.length !== editCourseTeachers.value.length || uniqueTeachers.some(tid => !tid)) {
    editCourseMsg.value = '请勿重复或留空任课教师'
    return
  }
  const timeStr = buildEditCourseTime()
  if (!timeStr) {
    editCourseMsg.value = '请选择上课周数和节次'
    return
  }
  const res = await axios.post('http://localhost:5000/api/teacher/edit_course', {
    course_id: editCourseId.value,
    name: editCourseName.value,
    credit: editCourseCredit.value,
    location: editCourseLocation.value,
    time: timeStr,
    teachers: uniqueTeachers,
    maxStudents: editCourseMaxStudents.value // 新增
  })
  if (res.data.success) {
    editCourseMsg.value = '修改成功'
    fetchCourses()
    setTimeout(() => { showEditCourseDialog.value = false }, 800)
  } else {
    editCourseMsg.value = res.data.message || '修改失败'
  }
}

// 删除任课弹窗
const openDeleteCourse = (item) => {
  deleteCourseId.value = item.course_id
  deleteCourseName.value = item.name
  deleteCourseMsg.value = ''
  showDelCourseDialog.value = true
}
const deleteCourse = async () => {
  const userId = localStorage.getItem('user_id')
  const res = await axios.post('http://localhost:5000/api/teacher/delete_course', {
    teacher_id: userId,
    course_id: deleteCourseId.value
  })
  if (res.data.success) {
    deleteCourseMsg.value = '删除成功'
    fetchCourses()
    setTimeout(() => { showDelCourseDialog.value = false }, 800)
  } else {
    deleteCourseMsg.value = res.data.message || '删除失败'
  }
}

// 创建并添加课程
const createAndAddCourse = async () => {
  if (
    !addCourseId.value ||
    !addCourseName.value ||
    !addCourseCredit.value ||
    !addCourseLocation.value ||
    !selectedWeeks.value.length ||
    !timeGroups.value.some(g => g.sections.length) ||
    !addCourseTeachers.value.length
  ) {
    addCourseMsg.value = '请填写完整课程信息'
    return
  }
  const userId = localStorage.getItem('user_id')
  const teachers = addCourseTeachers.value.filter(Boolean)
  const uniqueTeachers = [...new Set(teachers)]
  if (!uniqueTeachers.includes(userId)) uniqueTeachers.push(userId)
  if (uniqueTeachers.length !== addCourseTeachers.value.length || uniqueTeachers.some(tid => !tid)) {
    addCourseMsg.value = '请勿重复或留空任课教师'
    return
  }
  if (!uniqueTeachers.includes(userId)) {
    uniqueTeachers.push(userId)
  }
  const timeStr = buildCourseTime()
  if (!timeStr) {
    addCourseMsg.value = '请选择上课周数和节次'
    return
  }
  const res = await axios.post('http://localhost:5000/api/teacher/create_and_add_course', {
    teacher_id: userId,
    course_id: addCourseId.value,
    name: addCourseName.value,
    credit: addCourseCredit.value,
    location: addCourseLocation.value,
    time: timeStr,
    teachers: uniqueTeachers,
    maxStudents: addCourseMaxStudents.value // 新增
  })
  if (res.data.success) {
    addCourseMsg.value = '添加成功'
    fetchCourses()
    setTimeout(() => { showAddCourseDialog.value = false }, 800)
    addCourseId.value = ''
    addCourseName.value = ''
    addCourseCredit.value = ''
    addCourseLocation.value = ''
    selectedWeeks.value = []
    timeGroups.value = [{ day: 1, sections: [] }]
    addCourseTeachers.value = [userId]   // 这里要重置为本人
    addCourseMaxStudents.value = '' // 新增：清空上限人数
  } else {
    addCourseMsg.value = res.data.message || '添加失败'
  }
}

const selectedWeeks = ref([]) // 周数
const timeGroups = ref([
  { day: 1, sections: [] }
])

function addTimeGroup() {
  timeGroups.value.push({ day: 1, sections: [] })
}
function removeTimeGroup(idx) {
  timeGroups.value.splice(idx, 1)
}

function addTeacherGroup() {
  addCourseTeachers.value.push('');
}
function removeTeacherGroup(idx) {
  // 只允许移除非本人
  if (addCourseTeachers.value[idx] !== userId) {
    addCourseTeachers.value.splice(idx, 1);
  }
}

// 构建 time 字符串
function buildCourseTime() {
  if (!selectedWeeks.value.length || !timeGroups.value.length) return ''
  const weeks = selectedWeeks.value.sort((a,b)=>a-b).join(',')
  // 例：1,2,3,4,5周:1(1,2);3(3,4)
  const timeStr = timeGroups.value
    .filter(g => g.sections.length)
    .map(g => `${g.day}(${g.sections.sort((a,b)=>a-b).join(',')})`)
    .join(';')
  if (!timeStr) return ''
  return `${weeks}周:${timeStr}`
}

// 自动刷新
watch(activeMenu, (val) => {
  if (val === 'course') {
    fetchCourses()
    fetchAllCourses()
    fetchAllTeachers()
  }
})
onMounted(() => {
  setAvatarUrl()
  fetchTeacherInfo()
  fetchCurrentHeadClass()
  fetchAllClasses()
  fetchClassStudents()
  fetchColleges()
  fetchAllCourses()
  fetchAllTeachers()
  if (!addCourseTeachers.value.includes(userId)) {
    addCourseTeachers.value = [userId]
  }
})

watch(currentHeadClass, (val) => {
  if (val) {
    fetchClassStudents()
  } else {
    classStudents.value = []
  }
})

// 叠课申请处理相关
const showOverlapDialog = ref(false)
const overlapApplications = ref([])

const openOverlapDialog = async () => {
  const res = await axios.get('http://localhost:5000/api/teacher/overlap_applications', {
    params: { teacher_id: userId }
  })
  if (res.data.success) overlapApplications.value = res.data.applications
  showOverlapDialog.value = true
}

const processOverlap = async (student_id, course_id, action) => {
  await axios.post('http://localhost:5000/api/teacher/process_overlap', {
    student_id,
    course_id,
    action
  })
  openOverlapDialog()
}
</script>

<style scoped>
/* 澶嶇敤 AdminDashboard.vue 鐨勬牱寮� */
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
.account-list {
  background: rgba(44, 62, 80, 0.85);
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
.account-id { font-weight: bold; color: #5dade2; width: 120px; text-align: left; }
.account-role { color: #90caf9; width: 120px; text-align: left; }
.account-action { width: 180px; text-align: left; }
.header-row span {
  font-weight: bold;
  background: rgba(93,173,226,0.10);
  color: #90caf9;
}
.account-item span {
  display: inline-block;
  vertical-align: middle;
}
.empty-tip { text-align: center; color: #90caf9; padding: 32px 0; }

.dialog-mask {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.dialog {
  background: rgba(44, 62, 80, 0.95);
  border-radius: 12px;
  padding: 24px;
  width: 98%;
  max-width: 800px; /* 澧炲ぇ瀹藉害 */
  max-height: 90vh;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  overflow-y: auto;  /* 鍐呭鍙粴鍔� */
}
.dialog h3 {
  margin: 0 0 16px 0;
  color: #5dade2;
  font-size: 22px;
  text-align: center;
}
.dialog label {
  display: block;
  margin-bottom: 8px;
  color: #eaf6fb;
  font-weight: bold;
}
.dialog input[type="text"],
.dialog input[type="password"],
.dialog select {
  width: 100%;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #5dade2;
  font-size: 18px;
  background: #232526;
  color: #eaf6fb;
  outline: none;
  margin-bottom: 16px;
}
.dialog .dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.dialog button {
  background: linear-gradient(90deg, #5dade2 0%, #90caf9 100%);
  color: #232526;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 18px;
  cursor: pointer;
  transition: background 0.2s;
  font-weight: bold;
  box-shadow: 0 2px 8px #2c3e50;
}
.dialog button:hover {
  background: linear-gradient(90deg, #90caf9 0%, #5dade2 100%);
  color: #232526;
}
.dialog-msg {
  margin-top: 12px;
  color: #90caf9;
  font-size: 16px;
  text-align: center;
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
  margin-right: 12px;
}
.add-btn {
  background: linear-gradient(90deg, #5dade2 0%, #90caf9 100%);
  color: #232526;
  border: none;
  border-radius: 6px;
  padding: 10px 20px;
  font-size: 18px;
  cursor: pointer;
  transition: background 0.2s;
  font-weight: bold;
  box-shadow: 0 2px 8px #2c3e50;
}
.add-btn:disabled {
  background: rgba(93, 173, 226, 0.5);
  cursor: not-allowed;
}
.del-btn {
  background: rgba(255, 118, 117, 0.8);
  color: #232526;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
  font-weight: bold;
  box-shadow: 0 2px 8px #2c3e50;
}
.del-btn:hover {
  background: rgba(255, 82, 82, 0.9);
}
.student-select-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  cursor: pointer;
  transition: background 0.2s;
}
.student-select-item:hover {
  background: rgba(93,173,226,0.10);
}
.student-select-item.selected {
  background: rgba(93,173,226,0.15);
  border-radius: 6px;
}
.search-btn {
  padding: 6px 16px;
  font-size: 15px;
  height: 36px;
  line-height: 1;
  margin-left: 8px;
}
.cell-wrap {
  white-space: pre-wrap;
  word-break: break-all;
  max-width: 180px;      
  max-height: 48px;      
  overflow-y: auto;
  display: block;
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
.overlap-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #2c3e50;
}
.small-btn {
  background: linear-gradient(90deg, #5dade2 0%, #90caf9 100%);
  color: #232526;
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
  font-weight: bold;
  box-shadow: 0 2px 8px #2c3e50;
}
.small-btn:hover {
  background: linear-gradient(90deg, #90caf9 0%, #5dade2 100%);
  color: #232526;
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