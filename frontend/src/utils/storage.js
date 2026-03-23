/**
 * 本地存储工具函数
 */

// Token 相关
export const tokenStorage = {
  get: () => localStorage.getItem('token'),
  set: (token) => localStorage.setItem('token', token),
  remove: () => localStorage.removeItem('token'),
};

// 用户信息相关
export const userStorage = {
  get: () => {
    const userInfo = localStorage.getItem('userInfo');
    return userInfo ? JSON.parse(userInfo) : null;
  },
  set: (userInfo) => localStorage.setItem('userInfo', JSON.stringify(userInfo)),
  remove: () => localStorage.removeItem('userInfo'),
};
