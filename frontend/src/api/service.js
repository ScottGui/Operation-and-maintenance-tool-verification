/**
 * 服务管理相关 API
 */
import request from './request';

export const serviceApi = {
  // 获取服务列表
  getList: (params) => request.get('/services', { params }),
  
  // 获取服务详情
  getDetail: (id) => request.get(`/services/${id}`),
  
  // 创建服务
  create: (data) => request.post('/services', data),
  
  // 更新服务
  update: (id, data) => request.put(`/services/${id}`, data),
  
  // 删除服务
  delete: (id) => request.delete(`/services/${id}`),
  
  // 获取服务类型列表
  getTypes: () => request.get('/services/types'),
  
  // 获取服务状态列表
  getStatuses: () => request.get('/services/statuses'),
  
  // 获取服务等级列表
  getLevels: () => request.get('/services/levels'),
};
