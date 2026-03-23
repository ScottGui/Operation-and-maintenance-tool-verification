/**
 * 常量定义
 */

// 工单状态
export const WORK_ORDER_STATUS = {
  DRAFT: { value: 'draft', label: '草稿', color: 'default' },
  PENDING: { value: 'pending', label: '待审批', color: 'warning' },
  APPROVED: { value: 'approved', label: '已审批', color: 'processing' },
  PROCESSING: { value: 'processing', label: '处理中', color: 'processing' },
  COMPLETED: { value: 'completed', label: '已完成', color: 'success' },
  CLOSED: { value: 'closed', label: '已关闭', color: 'default' },
  REJECTED: { value: 'rejected', label: '已驳回', color: 'error' },
};

// 工单优先级
export const WORK_ORDER_PRIORITY = {
  URGENT: { value: 'urgent', label: '紧急', color: 'red' },
  HIGH: { value: 'high', label: '高', color: 'orange' },
  MEDIUM: { value: 'medium', label: '中', color: 'blue' },
  LOW: { value: 'low', label: '低', color: 'green' },
};

// 工单类型
export const WORK_ORDER_TYPE = {
  PLATFORM_BUILD: { value: 'platform_build', label: '平台建设' },
  PLATFORM_UPDATE: { value: 'platform_update', label: '平台迭代' },
  PLATFORM_OFFLINE: { value: 'platform_offline', label: '平台下线' },
  DATA_SERVICE_BUILD: { value: 'data_service_build', label: '数据服务建设' },
  DATA_SERVICE_UPDATE: { value: 'data_service_update', label: '数据服务迭代' },
  DATA_SERVICE_OFFLINE: { value: 'data_service_offline', label: '数据服务下线' },
  SECURITY: { value: 'security', label: '安全加固' },
  AUDIT: { value: 'audit', label: '审计管理' },
  RESOURCE: { value: 'resource', label: '资源申请' },
  OTHER: { value: 'other', label: '其他' },
};

// 资产状态
export const ASSET_STATUS = {
  IN_USE: { value: 'in_use', label: '在用', color: 'success' },
  IDLE: { value: 'idle', label: '闲置', color: 'default' },
  MAINTENANCE: { value: 'maintenance', label: '维护中', color: 'warning' },
  RETIRED: { value: 'retired', label: '已下线', color: 'error' },
  RESERVED: { value: 'reserved', label: '预留', color: 'processing' },
};

// 资产类型
export const ASSET_TYPE = {
  SERVER: { value: 'server', label: '服务器' },
  DATABASE: { value: 'database', label: '数据库' },
  MIDDLEWARE: { value: 'middleware', label: '中间件' },
  NETWORK: { value: 'network', label: '网络设备' },
  STORAGE: { value: 'storage', label: '存储设备' },
  SECURITY: { value: 'security', label: '安全设备' },
  SOFTWARE: { value: 'software', label: '软件' },
  OTHER: { value: 'other', label: '其他' },
};

// 服务状态
export const SERVICE_STATUS = {
  RUNNING: { value: 'running', label: '运行中', color: 'success' },
  STOPPED: { value: 'stopped', label: '已停止', color: 'error' },
  MAINTENANCE: { value: 'maintenance', label: '维护中', color: 'warning' },
  DEPRECATED: { value: 'deprecated', label: '已弃用', color: 'default' },
};

// 服务类型
export const SERVICE_TYPE = {
  PLATFORM: { value: 'platform', label: '平台服务' },
  DATA_SERVICE: { value: 'data_service', label: '数据服务' },
  SECURITY: { value: 'security', label: '安全服务' },
  MONITOR: { value: 'monitor', label: '监控服务' },
  TOOL: { value: 'tool', label: '工具服务' },
  OTHER: { value: 'other', label: '其他' },
};

// 服务等级
export const SERVICE_LEVEL = {
  P0: { value: 'p0', label: 'P0-核心服务', color: 'red' },
  P1: { value: 'p1', label: 'P1-重要服务', color: 'orange' },
  P2: { value: 'p2', label: 'P2-一般服务', color: 'blue' },
  P3: { value: 'p3', label: 'P3-低优先级', color: 'green' },
};
