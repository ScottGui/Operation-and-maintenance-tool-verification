/**
 * 常量定义
 */

// 需求单状态（对应10个流程节点）
export const WORK_ORDER_STATUS = {
  DRAFT: { value: 'draft', label: '草稿', color: 'default' },
  PENDING_REVIEW: { value: 'pending_review', label: '待审批', color: 'warning' },
  ANALYZED: { value: 'analyzed', label: '已梳理', color: 'processing' },
  APPROVED: { value: 'approved', label: '审批通过', color: 'success' },
  REJECTED: { value: 'rejected', label: '已驳回', color: 'error' },
  SOLUTION_SUBMITTED: { value: 'solution_submitted', label: '方案已提交', color: 'processing' },
  IN_REVIEW: { value: 'in_review', label: '会审中', color: 'warning' },
  IN_PROGRESS: { value: 'in_progress', label: '实施中', color: 'processing' },
  PENDING_QA: { value: 'pending_qa', label: '待质量稽核', color: 'warning' },
  PENDING_TRIAL: { value: 'pending_trial', label: '待试运行', color: 'warning' },
  PENDING_MONITOR: { value: 'pending_monitor', label: '待监控配置', color: 'warning' },
  ONLINE: { value: 'online', label: '已上线', color: 'success' },
};

// 需求单优先级
export const WORK_ORDER_PRIORITY = {
  URGENT: { value: 'urgent', label: '紧急', color: 'red' },
  HIGH: { value: 'high', label: '高', color: 'orange' },
  MEDIUM: { value: 'medium', label: '中', color: 'blue' },
  LOW: { value: 'low', label: '低', color: 'green' },
};

// 需求单类型
export const WORK_ORDER_TYPE = {
  INTERFACE_DEV: { value: 'interface_dev', label: '接口开发' },
  DATA_EXPORT: { value: 'data_export', label: '数据导出' },
  DATA_SYNC: { value: 'data_sync', label: '数据同步' },
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
