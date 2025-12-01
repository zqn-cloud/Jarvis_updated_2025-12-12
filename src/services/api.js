/**
 * Jarvis Calendar API Service
 * 连接Django后端的API服务
 */

// 本地开发使用 localhost，外部访问时替换为 Cloudflare Tunnel URL
// 例如: 'https://xxx-xxx-xxx.trycloudflare.com/api/v1'
const API_BASE_URL = window.JARVIS_API_URL || 'http://localhost:8000/api/v1';

// 存储token
let accessToken = localStorage.getItem('jarvis_access_token') || null;

/**
 * 设置访问令牌
 */
export const setAccessToken = (token) => {
  accessToken = token;
  if (token) {
    localStorage.setItem('jarvis_access_token', token);
  } else {
    localStorage.removeItem('jarvis_access_token');
  }
};

/**
 * 获取访问令牌
 */
export const getAccessToken = () => accessToken;

/**
 * 通用请求方法
 */
const request = async (endpoint, options = {}) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      headers,
    });
    
    const data = await response.json();
    
    if (!response.ok) {
      throw {
        status: response.status,
        ...data
      };
    }
    
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

/**
 * 文件上传请求
 */
const uploadRequest = async (endpoint, file) => {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const formData = new FormData();
  formData.append('file', file);
  
  const headers = {};
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }
  
  const response = await fetch(url, {
    method: 'POST',
    headers,
    body: formData,
  });
  
  const data = await response.json();
  
  if (!response.ok) {
    throw { status: response.status, ...data };
  }
  
  return data;
};

// ==================== AUTH ====================

export const authAPI = {
  /**
   * 登录
   */
  login: async (accountId) => {
    const result = await request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ account_id: accountId }),
    });
    
    if (result.success && result.data.access_token) {
      setAccessToken(result.data.access_token);
    }
    
    return result;
  },
  
  /**
   * 登出
   */
  logout: async () => {
    try {
      await request('/auth/logout', { method: 'POST' });
    } finally {
      setAccessToken(null);
    }
  },
};

// ==================== TIME ====================

export const timeAPI = {
  /**
   * 获取服务器时间
   */
  getServerTime: () => request('/time'),
};

// ==================== USER ====================

export const userAPI = {
  /**
   * 获取用户信息
   */
  getUser: () => request('/user'),
  
  /**
   * 更新用户信息
   */
  updateUser: (data) => request('/user', {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  
  /**
   * 获取用户位置
   */
  getLocation: () => request('/user/location'),
  
  /**
   * 更新用户位置
   */
  updateLocation: (latitude, longitude, accuracy = null) => request('/user/location', {
    method: 'POST',
    body: JSON.stringify({ latitude, longitude, accuracy }),
  }),
};

// ==================== CALENDAR TYPES ====================

export const calendarTypesAPI = {
  /**
   * 获取所有日历类型
   */
  getAll: () => request('/calendar-types'),
  
  /**
   * 创建日历类型
   */
  create: (name, color) => request('/calendar-types', {
    method: 'POST',
    body: JSON.stringify({ name, color }),
  }),
  
  /**
   * 更新日历类型
   */
  update: (typeId, data) => request(`/calendar-types/${typeId}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  
  /**
   * 切换可见性
   */
  toggleVisibility: (typeId, isVisible) => request(`/calendar-types/${typeId}/visibility`, {
    method: 'PATCH',
    body: JSON.stringify({ is_visible: isVisible }),
  }),
  
  /**
   * 删除日历类型
   */
  delete: (typeId) => request(`/calendar-types/${typeId}`, {
    method: 'DELETE',
  }),
};

// ==================== EVENTS ====================

export const eventsAPI = {
  /**
   * 获取事件列表
   */
  getAll: (params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.date) queryParams.append('date', params.date);
    if (params.start_date) queryParams.append('start_date', params.start_date);
    if (params.end_date) queryParams.append('end_date', params.end_date);
    if (params.type_id) queryParams.append('type_id', params.type_id);
    if (params.completed !== undefined) queryParams.append('completed', params.completed);
    
    const queryString = queryParams.toString();
    return request(`/events${queryString ? '?' + queryString : ''}`);
  },
  
  /**
   * 获取单个事件
   */
  get: (eventId) => request(`/events/${eventId}`),
  
  /**
   * 创建事件
   */
  create: (eventData) => request('/events', {
    method: 'POST',
    body: JSON.stringify(eventData),
  }),
  
  /**
   * 更新事件
   */
  update: (eventId, eventData) => request(`/events/${eventId}`, {
    method: 'PUT',
    body: JSON.stringify(eventData),
  }),
  
  /**
   * 删除事件
   */
  delete: (eventId) => request(`/events/${eventId}`, {
    method: 'DELETE',
  }),
  
  /**
   * 切换完成状态
   */
  toggleComplete: (eventId, completed) => request(`/events/${eventId}/complete`, {
    method: 'PATCH',
    body: JSON.stringify({ completed }),
  }),
  
  /**
   * 添加链接
   */
  addLink: (eventId, url) => request(`/events/${eventId}/links`, {
    method: 'POST',
    body: JSON.stringify({ url }),
  }),
  
  /**
   * 删除链接
   */
  removeLink: (eventId, url) => request(`/events/${eventId}/links`, {
    method: 'DELETE',
    body: JSON.stringify({ url }),
  }),
};

// ==================== FILES ====================

export const filesAPI = {
  /**
   * 上传文件
   */
  upload: (file) => uploadRequest('/files/upload', file),
  
  /**
   * 删除文件
   */
  delete: (fileId) => request(`/files/${fileId}`, {
    method: 'DELETE',
  }),
};

// ==================== REMINDERS ====================

export const remindersAPI = {
  /**
   * 获取提醒
   */
  getAll: (date = null) => {
    const queryString = date ? `?date=${date}` : '';
    return request(`/reminders${queryString}`);
  },
};

// ==================== COMMUTE ====================

export const commuteAPI = {
  /**
   * 获取通勤信息
   */
  get: (from = 'home', to = 'school') => {
    return request(`/location/commute?from=${from}&to=${to}`);
  },
};

// 导出所有API
export default {
  auth: authAPI,
  time: timeAPI,
  user: userAPI,
  calendarTypes: calendarTypesAPI,
  events: eventsAPI,
  files: filesAPI,
  reminders: remindersAPI,
  commute: commuteAPI,
  setAccessToken,
  getAccessToken,
};

