/**
 * 用户管理API封装
 * 
 * 包含接口：
 * - 创建用户
 * - 获取用户列表（支持分页、搜索、筛选）
 * - 获取用户详情
 * - 更新用户
 * - 删除用户（软删除）
 * 
 * 作者/日期：AI / 2026-03-24
 */

import request from './request';

/**
 * 用户管理API
 */
export const userApi = {
  /**
   * 创建用户
   * @param {Object} data - 用户数据
   * @returns {Promise}
   */
  create: (data) => request.post('/users', data),
  
  /**
   * 获取用户列表
   * @param {Object} params - 查询参数
   * @returns {Promise}
   */
  getList: (params) => request.get('/users', { params }),
  
  /**
   * 获取用户详情
   * @param {number} id - 用户ID
   * @returns {Promise}
   */
  getById: (id) => request.get(`/users/${id}`),
  
  /**
   * 更新用户
   * @param {number} id - 用户ID
   * @param {Object} data - 更新数据
   * @returns {Promise}
   */
  update: (id, data) => request.put(`/users/${id}`, data),
  
  /**
   * 删除用户（软删除）
   * @param {number} id - 用户ID
   * @returns {Promise}
   */
  delete: (id) => request.delete(`/users/${id}`),
};

// 兼容旧代码的独立导出
export const createUser = (data) => userApi.create(data);
export const getUserList = (params) => userApi.getList(params);
export const getUserDetail = (id) => userApi.getById(id);
export const updateUser = (id, data) => userApi.update(id, data);
export const deleteUser = (id) => userApi.delete(id);

/**
 * 角色选项（7个业务角色，不包含管理员）
 * 用于前端下拉选择
 */
export const ROLE_OPTIONS = [
  { value: 'data_consumer', label: '用数方' },
  { value: 'requirement_manager', label: '需求经理' },
  { value: 'operator', label: '运营方' },
  { value: 'project_manager', label: '项目经理' },
  { value: 'qa_manager', label: '质量稽核经理' },
  { value: 'ops_manager', label: '数据运维经理' },
  { value: 'team_lead', label: '四方组长' },
];

/**
 * 状态选项
 */
export const STATUS_OPTIONS = [
  { value: 'active', label: '启用' },
  { value: 'inactive', label: '禁用' },
];
