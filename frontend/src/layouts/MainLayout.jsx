/**
 * 主布局组件
 * 包含侧边栏导航和顶部栏
 */
import { useState, useEffect } from 'react';
import { Layout, Menu, Avatar, Dropdown, Button, message, Popconfirm } from 'antd';
import {
  DashboardOutlined,
  FileTextOutlined,
  DatabaseOutlined,
  CloudServerOutlined,
  TeamOutlined,
  LogoutOutlined,
  UserOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { userStorage, tokenStorage } from '../utils/storage';
import './MainLayout.css';

const { Header, Sider, Content } = Layout;

const MainLayout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [userInfo, setUserInfo] = useState(null);

  // 获取用户信息
  useEffect(() => {
    const user = userStorage.get();
    if (!user) {
      navigate('/login');
      return;
    }
    setUserInfo(user);
  }, [navigate]);

  // 菜单项
  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '仪表盘',
    },
    {
      key: '/work-orders',
      icon: <FileTextOutlined />,
      label: '需求单管理',
    },
    {
      key: '/assets',
      icon: <DatabaseOutlined />,
      label: '资产管理',
    },
    {
      key: '/services',
      icon: <CloudServerOutlined />,
      label: '服务管理',
    },
    {
      key: '/users',
      icon: <TeamOutlined />,
      label: '用户管理',
    },
    {
      key: '/files',
      icon: <FileTextOutlined />,
      label: '文档管理',
    },
  ];

  // 处理菜单点击
  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  // 处理登出
  const handleLogout = () => {
    tokenStorage.remove();
    userStorage.remove();
    message.success('已退出登录');
    navigate('/login');
  };

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

  // 获取当前选中的菜单
  const getSelectedKey = () => {
    const path = location.pathname;
    if (path === '/') return '/';
    const menuKey = menuItems.find(item => path.startsWith(item.key))?.key;
    return menuKey || '/';
  };

  return (
    <Layout className="main-layout">
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        theme="light"
        className="main-sider"
      >
        <div className="logo">
          <img src="/favicon.svg" alt="logo" />
          {!collapsed && <span>运维平台</span>}
        </div>
        <Menu
          mode="inline"
          selectedKeys={[getSelectedKey()]}
          items={menuItems}
          onClick={handleMenuClick}
          className="main-menu"
        />
      </Sider>
      
      <Layout>
        <Header className="main-header">
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            className="collapse-btn"
          />
          
          <div className="header-right">
            <Dropdown
              menu={{
                items: [
                  {
                    key: 'user-info',
                    label: (
                      <div style={{ padding: '4px 0' }}>
                        <div style={{ fontWeight: 500 }}>{userInfo?.real_name}</div>
                        <div style={{ fontSize: '12px', color: '#8c8c8c' }}>
                          {getRoleDisplay(userInfo?.role)}
                        </div>
                      </div>
                    ),
                    disabled: true,
                  },
                  {
                    type: 'divider',
                  },
                  {
                    key: 'logout',
                    label: (
                      <Popconfirm
                        title="确定要退出登录吗？"
                        onConfirm={handleLogout}
                        okText="确定"
                        cancelText="取消"
                        placement="bottomRight"
                      >
                        <span>
                          <LogoutOutlined style={{ marginRight: 8 }} />
                          退出登录
                        </span>
                      </Popconfirm>
                    ),
                  },
                ],
              }}
              placement="bottomRight"
            >
              <div className="user-info" style={{ cursor: 'pointer', padding: '4px 8px', borderRadius: 4 }}>
                <Avatar 
                  icon={<UserOutlined />} 
                  style={{ backgroundColor: userInfo?.role === 'admin' ? '#f5222d' : '#1890ff' }}
                />
                <span className="username" style={{ marginLeft: 8, marginRight: 4 }}>
                  {userInfo?.real_name || userInfo?.username}
                </span>
                <span style={{ fontSize: 12, color: '#8c8c8c' }}>
                  ({getRoleDisplay(userInfo?.role)})
                </span>
              </div>
            </Dropdown>
          </div>
        </Header>
        
        <Content className="main-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
