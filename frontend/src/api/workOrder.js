/**
 * 工单管理相关 API
 */
import request from './request';

export const workOrderApi = {
  // 获取工单列表
  getList: (params) => request.get('/work-orders', { params }),
  
  // 获取工单详情
  getDetail: (id) => request.get(`/work-orders/${id}`),
  
  // 创建工单
  create: (data) => request.post('/work-orders', data),
  
  // 更新工单
  update: (id, data) => request.put(`/work-orders/${id}`, data),
  
  // 删除工单
  delete: (id) => request.delete(`/work-orders/${id}`),
  
  // 提交工单审批
  submit: (id) => request.post(`/work-orders/${id}/submit`),
  
  // 审批工单
  approve: (id, data) => request.post(`/work-orders/${id}/approve`, data),
  
  // 分配工单
  assign: (id, data) => request.post(`/work-orders/${id}/assign`, data),
  
  // 开始处理工单
  start: (id) => request.post(`/work-orders/${id}/start`),
  
  // 完成工单
  complete: (id, data) => request.post(`/work-orders/${id}/complete`, data),
  
  // 关闭工单
  close: (id, data) => request.post(`/work-orders/${id}/close`, data),
  
  // 获取工单流转记录
  getFlows: (id) => request.get(`/work-orders/${id}/flows`),
};
