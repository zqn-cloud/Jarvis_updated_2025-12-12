export const mockTasks = [
  {
    id: '1',
    title: 'KAI BIRTHDAY TOMORROW',
    isAllDay: true,
    date: new Date(), // Today
    color: '#F59E0B', // Events orange
    completed: false,
    type: 'event'
  },
  {
    id: '2',
    title: 'SIGN UP TO UNI',
    isAllDay: true,
    date: new Date(),
    color: '#F59E0B',
    completed: true,
    attachment: { name: 'Docs.pdf', url: '#' },
    type: 'event'
  },
  {
    id: '3',
    title: 'Therapy',
    isAllDay: false,
    startTime: '15:00',
    endTime: '17:00',
    timeRange: '3PM to 5PM',
    date: new Date(),
    color: '#EC4899', // Routine pink
    completed: false,
    location: 'Clinic',
    type: 'routine'
  },
  {
    id: '4',
    title: 'School Project',
    isAllDay: false,
    startTime: '09:00',
    endTime: '12:00',
    timeRange: '9AM to 12PM',
    date: new Date(),
    color: '#22C55E', // School green
    completed: false,
    type: 'school'
  }
];

export const mockReminders = [
  {
    id: 'weather',
    type: 'weather',
    title: '今日天气',
    subtitle: '多云转晴, 18°C - 25°C, 适合外出',
    icon: 'cloud',
    color: '#EAF2FD',
    iconColor: '#3B82F6'
  },
  {
    id: 'commute',
    type: 'commute',
    title: '通勤信息',
    subtitle: '前往学校约需 25 分钟，距离 8.5 公里',
    icon: 'navigation',
    color: '#E8F5E9',
    iconColor: '#22C55E'
  },
  {
    id: 'birthday',
    type: 'important',
    title: '重要提醒',
    subtitle: '明天是 Kai 的生日，记得准备礼物 🎁',
    icon: 'calendar',
    color: '#FCE4EC',
    iconColor: '#EC4899'
  }
];

