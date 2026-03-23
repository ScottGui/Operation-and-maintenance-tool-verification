/**
 * 统计相关 API
 */
import request from './request';

export const statisticsApi = {
  // 获取仪表盘统计数据
  getDashboard: () => request.get('/statistics/dashboard'),
  
  // 获取工单统计
  getWorkOrderStats: (params) => request.get('/statistics/work-orders', { params }),
  
  // 获取资产统计
  getAssetStats: () => request.get('/statistics/assets'),
  
  // 获取服务统计
  getServiceStats: () => request.get('/statistics/services'),
};
