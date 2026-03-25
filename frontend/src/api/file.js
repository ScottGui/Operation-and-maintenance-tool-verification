/**
 * 文件管理API
 * 
 * 作者/日期：AI / 2026-03-25
 */

import request from './request';

export const fileApi = {
  /**
   * 上传文件
   * @param {FormData} formData - 包含文件的FormData
   * @param {number} orderId - 关联的需求单ID（可选）
   * @returns {Promise}
   */
  upload: (formData, orderId = null) => {
    const url = orderId ? `/files/upload?order_id=${orderId}` : '/files/upload';
    return request.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  /**
   * 获取文件列表
   * @param {number} orderId - 按需求单ID筛选（可选）
   * @returns {Promise}
   */
  getList: (orderId = null) => {
    const url = orderId ? `/files?order_id=${orderId}` : '/files';
    return request.get(url);
  },
  
  /**
   * 删除文件
   * @param {number} fileId - 文件ID
   * @returns {Promise}
   */
  delete: (fileId) => request.delete(`/files/${fileId}`),
  
  /**
   * 下载文件（返回下载链接）
   * @param {number} fileId - 文件ID
   * @returns {string} 下载URL
   */
  getDownloadUrl: (fileId) => {
    return `http://localhost:8000/api/files/${fileId}/download`;
  },
};

/**
 * 文件类型配置
 */
export const FILE_TYPE_CONFIG = {
  pdf: { icon: 'file-pdf', color: '#ff4d4f', label: 'PDF' },
  doc: { icon: 'file-word', color: '#1890ff', label: 'Word' },
  docx: { icon: 'file-word', color: '#1890ff', label: 'Word' },
  xls: { icon: 'file-excel', color: '#52c41a', label: 'Excel' },
  xlsx: { icon: 'file-excel', color: '#52c41a', label: 'Excel' },
  image: { icon: 'file-image', color: '#722ed1', label: '图片' },
};

/**
 * 获取文件类型配置
 * @param {string} fileType - 文件类型
 * @returns {Object}
 */
export const getFileTypeConfig = (fileType) => {
  return FILE_TYPE_CONFIG[fileType] || { icon: 'file', color: '#8c8c8c', label: '文件' };
};
