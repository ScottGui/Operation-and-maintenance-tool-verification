/**
 * 仪表盘页面
 * 展示系统概览统计数据
 */
import { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Badge, Table, Tag } from 'antd';
import {
  FileTextOutlined,
  DatabaseOutlined,
  CloudServerOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons';
import { statisticsApi } from '../../api';
import {
  WORK_ORDER_STATUS,
  WORK_ORDER_PRIORITY,
} from '../../utils/constants';
import './style.css';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    work_orders: { total: 0, pending: 0, processing: 0, closed_today: 0 },
    assets: { total: 0, in_use: 0, maintenance: 0 },
    services: { total: 0, running: 0, maintenance: 0 },
    recent_work_orders: [],
  });

  // 获取统计数据
  const fetchStats = async () => {
    try {
      setLoading(true);
      const res = await statisticsApi.getDashboard();
      setStats(res.data);
    } catch (error) {
      console.error('获取统计数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  // 获取状态标签
  const getStatusTag = (status) => {
    const config = WORK_ORDER_STATUS[status?.toUpperCase()];
    if (!config) return <Tag>{status}</Tag>;
    return <Badge status={config.color} text={config.label} />;
  };

  // 获取优先级标签
  const getPriorityTag = (priority) => {
    const config = WORK_ORDER_PRIORITY[priority?.toUpperCase()];
    if (!config) return <Tag>{priority}</Tag>;
    return <Tag color={config.color}>{config.label}</Tag>;
  };

  // 最近工单表格列
  const workOrderColumns = [
    {
      title: '工单编号',
      dataIndex: 'order_no',
      key: 'order_no',
      width: 160,
    },
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      ellipsis: true,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: getStatusTag,
    },
    {
      title: '创建人',
      dataIndex: 'creator_name',
      key: 'creator_name',
      width: 120,
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text) => text ? new Date(text).toLocaleString() : '-',
    },
  ];

  return (
    <div className="dashboard">
      <h2 className="page-title">仪表盘</h2>
      
      {/* 统计卡片 */}
      <Row gutter={[24, 24]} className="stats-row">
        <Col xs={24} sm={12} lg={8}>
          <Card loading={loading} className="stat-card">
            <Statistic
              title="工单总数"
              value={stats.work_orders.total}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <div className="stat-detail">
              <span>
                <ClockCircleOutlined /> 待处理: {stats.work_orders.pending}
              </span>
              <span>
                <SyncOutlined /> 处理中: {stats.work_orders.processing}
              </span>
            </div>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={8}>
          <Card loading={loading} className="stat-card">
            <Statistic
              title="资产总数"
              value={stats.assets.total}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <div className="stat-detail">
              <span>
                <CheckCircleOutlined /> 在用: {stats.assets.in_use}
              </span>
              <span>
                <SyncOutlined /> 维护中: {stats.assets.maintenance}
              </span>
            </div>
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={8}>
          <Card loading={loading} className="stat-card">
            <Statistic
              title="服务总数"
              value={stats.services.total}
              prefix={<CloudServerOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
            <div className="stat-detail">
              <span>
                <CheckCircleOutlined /> 运行中: {stats.services.running}
              </span>
              <span>
                <SyncOutlined /> 维护中: {stats.services.maintenance}
              </span>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 最近工单 */}
      <Card
        title="最近工单"
        loading={loading}
        className="recent-orders-card"
      >
        <Table
          columns={workOrderColumns}
          dataSource={stats.recent_work_orders}
          rowKey="id"
          pagination={false}
          size="small"
        />
      </Card>
    </div>
  );
};

export default Dashboard;
