/**
 * 资产管理相关 API
 */
import request from './request';

export const assetApi = {
  // 获取资产列表
  getList: (params) => request.get('/assets', { params }),
  
  // 获取资产详情
  getDetail: (id) => request.get(`/assets/${id}`),
  
  // 创建资产
  create: (data) => request.post('/assets', data),
  
  // 更新资产
  update: (id, data) => request.put(`/assets/${id}`, data),
  
  // 删除资产
  delete: (id) => request.delete(`/assets/${id}`),
  
  // 获取资产类型列表
  getTypes: () => request.get('/assets/types'),
  
  // 获取资产状态列表
  getStatuses: () => request.get('/assets/statuses'),
};
