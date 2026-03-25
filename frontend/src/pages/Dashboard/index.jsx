/**
 * 工作台页面（角色差异化）
 * 
 * 根据用户角色显示不同的统计、快捷入口和待办事项
 * MVP简化版，P1阶段增加流程可视化大屏
 * 
 * 作者/日期：AI / 2026-03-25
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Row,
  Col,
  Statistic,
  Button,
  List,
  Tag,
  Skeleton,
  Empty,
} from 'antd';
import {
  FileTextOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  UserOutlined,
  BarChartOutlined,
  PlusOutlined,
  UnorderedListOutlined,
  AuditOutlined,
  ToolOutlined,
} from '@ant-design/icons';
import { dashboardApi } from '../../api';
import { userStorage } from '../../utils/storage';
import './style.css';

const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});
  const [todos, setTodos] = useState([]);
  const [userInfo, setUserInfo] = useState(null);

  // 获取用户信息
  useEffect(() => {
    const user = userStorage.get();
    setUserInfo(user);
  }, []);

  // 获取工作台数据
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, todosRes] = await Promise.all([
          dashboardApi.getStats(),
          dashboardApi.getTodos(),
        ]);
        
        if (statsRes.data?.code === 200) {
          setStats(statsRes.data.data);
        }
        
        if (todosRes.data?.code === 200) {
          setTodos(todosRes.data.data);
        }
      } catch (error) {
        console.error('获取工作台数据失败:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // 获取角色显示名称
  const getRoleDisplay = (role) => {
    const roleMap = {
      'admin': '管理员',
      'data_consumer': '用数方',
      'requirement_manager': '需求经理',
      'operator': '运营方',
      'project_manager': '项目经理',
      'qa_manager': '质量稽核经理',
      'ops_manager': '数据运维经理',
      'team_lead': '四方组长',
    };
    return roleMap[role] || role;
  };

  // 根据角色获取统计卡片配置
  const getStatsConfig = (role) => {
    const configs = {
      data_consumer: [
        { key: 'myTodo', title: '我的待办', icon: <ClockCircleOutlined />, color: '#faad14' },
        { key: 'myOrders', title: '我的需求', icon: <FileTextOutlined />, color: '#1890ff' },
        { key: 'completed', title: '已完成', icon: <CheckCircleOutlined />, color: '#52c41a' },
      ],
      requirement_manager: [
        { key: 'pendingAnalysis', title: '待梳理', icon: <ClockCircleOutlined />, color: '#faad14' },
        { key: 'myAnalysis', title: '我的梳理', icon: <FileTextOutlined />, color: '#1890ff' },
        { key: 'submitted', title: '已提交', icon: <CheckCircleOutlined />, color: '#52c41a' },
      ],
      operator: [
        { key: 'pendingApproval', title: '待审批', icon: <ClockCircleOutlined />, color: '#faad14' },
        { key: 'pendingReview', title: '待会审', icon: <AuditOutlined />, color: '#722ed1' },
        { key: 'processed', title: '已处理', icon: <CheckCircleOutlined />, color: '#52c41a' },
        { key: 'todayStats', title: '今日统计', icon: <BarChartOutlined />, color: '#13c2c2' },
      ],
      project_manager: [
        { key: 'pendingClaim', title: '待认领', icon: <ClockCircleOutlined />, color: '#faad14' },
        { key: 'inProgress', title: '进行中', icon: <ToolOutlined />, color: '#1890ff' },
        { key: 'delivered', title: '已交付', icon: <CheckCircleOutlined />, color: '#52c41a' },
      ],
      qa_manager: [
        { key: 'pendingQA', title: '待稽核', icon: <ClockCircleOutlined />, color: '#faad14' },
        { key: 'completedQA', title: '已稽核', icon: <CheckCircleOutlined />, color: '#52c41a' },
        { key: 'passRate', title: '通过率', icon: <BarChartOutlined />, color: '#13c2c2' },
      ],
      ops_manager: [
        { key: 'pendingTrial', title: '待试运行', icon: <ClockCircleOutlined />, color: '#faad14' },
        { key: 'pendingMonitor', title: '待配置监控', icon: <ToolOutlined />, color: '#1890ff' },
        { key: 'online', title: '已上线', icon: <CheckCircleOutlined />, color: '#52c41a' },
        { key: 'overview', title: '全局概览', icon: <BarChartOutlined />, color: '#13c2c2' },
      ],
      team_lead: [
        { key: 'pendingReview', title: '待会审', icon: <ClockCircleOutlined />, color: '#faad14' },
        { key: 'completedReview', title: '已会审', icon: <CheckCircleOutlined />, color: '#52c41a' },
      ],
      admin: [
        { key: 'totalUsers', title: '总用户数', icon: <UserOutlined />, color: '#1890ff' },
        { key: 'totalOrders', title: '总需求数', icon: <FileTextOutlined />, color: '#722ed1' },
        { key: 'onlineServices', title: '在线服务', icon: <CheckCircleOutlined />, color: '#52c41a' },
        { key: 'systemStatus', title: '系统状态', icon: <BarChartOutlined />, color: '#13c2c2' },
      ],
    };
    return configs[role] || [];
  };

  // 根据角色获取快捷按钮配置
  const getQuickActions = (role) => {
    const actions = {
      data_consumer: [
        { label: '发起需求', icon: <PlusOutlined />, path: '/work-orders/create' },
        { label: '查看我的需求', icon: <UnorderedListOutlined />, path: '/work-orders' },
      ],
      requirement_manager: [
        { label: '查看待梳理', icon: <ClockCircleOutlined />, path: '/work-orders' },
        { label: '查看需求池', icon: <UnorderedListOutlined />, path: '/work-orders' },
      ],
      operator: [
        { label: '待审批列表', icon: <ClockCircleOutlined />, path: '/work-orders' },
        { label: '待会审列表', icon: <AuditOutlined />, path: '/work-orders' },
        { label: '报表中心', icon: <BarChartOutlined />, path: '/statistics' },
      ],
      project_manager: [
        { label: '查看待认领', icon: <ClockCircleOutlined />, path: '/work-orders' },
        { label: '查看实施中', icon: <ToolOutlined />, path: '/work-orders' },
      ],
      qa_manager: [
        { label: '待稽核列表', icon: <ClockCircleOutlined />, path: '/work-orders' },
        { label: '稽核历史', icon: <CheckCircleOutlined />, path: '/work-orders' },
      ],
      ops_manager: [
        { label: '待试运行', icon: <ClockCircleOutlined />, path: '/work-orders' },
        { label: '监控配置', icon: <ToolOutlined />, path: '/services' },
        { label: '服务台账', icon: <UnorderedListOutlined />, path: '/services' },
      ],
      team_lead: [
        { label: '待会审列表', icon: <ClockCircleOutlined />, path: '/work-orders' },
        { label: '会审历史', icon: <CheckCircleOutlined />, path: '/work-orders' },
      ],
      admin: [
        { label: '用户管理', icon: <UserOutlined />, path: '/users' },
        { label: '查看所有需求', icon: <UnorderedListOutlined />, path: '/work-orders' },
      ],
    };
    return actions[role] || [];
  };

  const statsConfig = getStatsConfig(userInfo?.role);
  const quickActions = getQuickActions(userInfo?.role);

  return (
    <div className="dashboard-page">
      {/* 欢迎区域 */}
      <div className="welcome-section">
        <h1>欢迎回来，{userInfo?.real_name || userInfo?.username}</h1>
        <Tag color="blue" className="role-tag">
          {getRoleDisplay(userInfo?.role)}
        </Tag>
      </div>

      {/* 统计卡片区域 */}
      <Row gutter={16} className="stats-section">
        {loading ? (
          <>
            {[1, 2, 3].map((i) => (
              <Col span={8} key={i}>
                <Card><Skeleton active /></Card>
              </Col>
            ))}
          </>
        ) : (
          statsConfig.map((item) => (
            <Col span={statsConfig.length === 4 ? 6 : 8} key={item.key}>
              <Card 
                className="stat-card" 
                hoverable
                onClick={() => {
                  // 根据卡片类型设置筛选参数
                  const filterMap = {
                    'myTodo': { status: 'pending_review' },
                    'myOrders': {},
                    'completed': { status: 'online' },
                  };
                  const filter = filterMap[item.key] || {};
                  const queryString = new URLSearchParams(filter).toString();
                  navigate(`/work-orders${queryString ? '?' + queryString : ''}`);
                }}
                style={{ cursor: 'pointer' }}
              >
                <Statistic
                  title={item.title}
                  value={stats[item.key] || 0}
                  valueStyle={{ color: item.color }}
                  prefix={item.icon}
                />
              </Card>
            </Col>
          ))
        )}
      </Row>

      {/* 快捷操作区域 */}
      <Card className="quick-actions-section" title="快捷操作">
        <div className="quick-actions">
          {quickActions.map((action, index) => (
            <Button
              key={index}
              type="primary"
              icon={action.icon}
              onClick={() => navigate(action.path)}
              className="action-btn"
            >
              {action.label}
            </Button>
          ))}
        </div>
      </Card>

      {/* 待办事项区域 */}
      <Card className="todo-section" title="我的待办">
        {loading ? (
          <Skeleton active />
        ) : todos.length > 0 ? (
          <List
            dataSource={todos}
            renderItem={(item) => (
              <List.Item
                actions={[
                  <Button 
                    type="link" 
                    size="small"
                    onClick={() => navigate('/work-orders')}
                  >
                    查看
                  </Button>,
                ]}
              >
                <List.Item.Meta
                  title={item.title}
                  description={
                    <span>
                      <Tag size="small">{item.type}</Tag>
                      <span className="create-time">{item.createTime}</span>
                    </span>
                  }
                />
              </List.Item>
            )}
          />
        ) : (
          <Empty description="暂无待办事项" />
        )}
      </Card>
    </div>
  );
};

export default Dashboard;
