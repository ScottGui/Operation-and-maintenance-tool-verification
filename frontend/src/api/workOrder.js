/**
 * 需求单管理相关 API
 */
import request from './request';

export const workOrderApi = {
  // 获取需求单列表
  getList: (params) => request.get('/work-orders', { params }),
  
  // 获取需求单详情
  getDetail: (id) => request.get(`/work-orders/${id}`),
  
  // 创建需求单
  create: (data) => request.post('/work-orders', data),
  
  // 更新需求单
  update: (id, data) => request.put(`/work-orders/${id}`, data),
  
  // 删除需求单
  delete: (id) => request.delete(`/work-orders/${id}`),
  
  // 提交需求单审批
  submit: (id) => request.post(`/work-orders/${id}/submit`),
  
  // 审批需求单
  approve: (id, data) => request.post(`/work-orders/${id}/approve`, data),
  
  // 分配需求单
  assign: (id, data) => request.post(`/work-orders/${id}/assign`, data),
  
  // 开始处理需求单
  start: (id) => request.post(`/work-orders/${id}/start`),
  
  // 完成需求单
  complete: (id, data) => request.post(`/work-orders/${id}/complete`, data),
  
  // 关闭需求单
  close: (id, data) => request.post(`/work-orders/${id}/close`, data),
  
  // 获取需求单流转记录
  getFlows: (id) => request.get(`/work-orders/${id}/flows`),
};
