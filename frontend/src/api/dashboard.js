/**
 * 工作台API
 * 
 * 作者/日期：AI / 2026-03-25
 */

import request from './request';

export const dashboardApi = {
  /**
   * 获取工作台统计数据
   * @returns {Promise}
   */
  getStats: () => request.get('/dashboard/stats'),
  
  /**
   * 获取待办事项列表
   * @returns {Promise}
   */
  getTodos: () => request.get('/dashboard/todos'),
};
