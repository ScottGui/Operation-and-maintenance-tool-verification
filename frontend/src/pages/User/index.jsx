/**
 * 用户管理页面
 * 
 * 功能：
 * - 用户列表展示（表格）
 * - 搜索（用户名/姓名）
 * - 筛选（角色、状态）
 * - 分页（每页20条）
 * - 新增用户
 * - 编辑用户
 * - 禁用/启用用户
 * 
 * 角色权限：仅管理员可见
 * 
 * 作者/日期：AI / 2026-03-24
 */

import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Input,
  Select,
  Space,
  Tag,
  Popconfirm,
  message,
  Row,
  Col,
} from 'antd';
import { PlusOutlined, SearchOutlined, EditOutlined, StopOutlined, CheckCircleOutlined, DeleteOutlined } from '@ant-design/icons';
import UserForm from './UserForm';
import { userApi, ROLE_OPTIONS, STATUS_OPTIONS } from '../../api/user';
import './style.css';

const { Option } = Select;

function UserManagement() {
  // ============== 状态管理 ==============
  const [loading, setLoading] = useState(false);
  const [dataSource, setDataSource] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });
  const [searchParams, setSearchParams] = useState({
    keyword: '',
    role: undefined,
    status: undefined,
  });
  
  // 弹窗状态
  const [modalVisible, setModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState('新增用户');
  const [editingUser, setEditingUser] = useState(null);

  // ============== 数据加载 ==============
  const fetchData = async (params = {}) => {
    setLoading(true);
    try {
      const response = await userApi.getList({
        page: pagination.current,
        page_size: pagination.pageSize,
        ...searchParams,
        ...params,
      });
      
      if (response.data?.code === 200) {
        const { total, items, page } = response.data.data;
        setDataSource(items);
        setPagination({
          ...pagination,
          total,
          current: page,
        });
      }
    } catch (error) {
      message.error('加载用户列表失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 页面初始化加载数据
  useEffect(() => {
    fetchData();
  }, []);

  // ============== 事件处理 ==============
  
  // 搜索
  const handleSearch = () => {
    setPagination({ ...pagination, current: 1 });
    fetchData({ page: 1 });
  };

  // 重置搜索
  const handleReset = () => {
    setSearchParams({
      keyword: '',
      role: undefined,
      status: undefined,
    });
    setPagination({ ...pagination, current: 1 });
    fetchData({
      page: 1,
      keyword: '',
      role: undefined,
      status: undefined,
    });
  };

  // 分页变化
  const handleTableChange = (newPagination) => {
    setPagination(newPagination);
    fetchData({
      page: newPagination.current,
      page_size: newPagination.pageSize,
    });
  };

  // 打开新增弹窗
  const handleAdd = () => {
    console.log('点击新增按钮');
    setModalTitle('新增用户');
    setEditingUser(null);
    setModalVisible(true);
    console.log('modalVisible 设置为 true');
  };

  // 打开编辑弹窗
  const handleEdit = (record) => {
    console.log('点击编辑按钮', record);
    setModalTitle('编辑用户');
    setEditingUser(record);
    setModalVisible(true);
  };

  // 弹窗关闭
  const handleModalClose = () => {
    setModalVisible(false);
    setEditingUser(null);
  };

  // 弹窗成功回调
  const handleModalSuccess = () => {
    setModalVisible(false);
    setEditingUser(null);
    fetchData();
  };

  // 删除用户
  const handleDelete = async (record) => {
    try {
      const response = await userApi.delete(record.id);
      
      if (response.data?.code === 200) {
        message.success('删除成功');
        fetchData(); // 刷新列表
      } else {
        message.error(response.data?.message || '删除失败');
      }
    } catch (error) {
      message.error(error.response?.data?.message || '删除失败');
      console.error(error);
    }
  };

  // 禁用/启用用户
  const handleToggleStatus = async (record) => {
    try {
      const newStatus = record.status === 'active' ? 'inactive' : 'active';
      const response = await userApi.update(record.id, { status: newStatus });
      
      if (response.data?.code === 200) {
        message.success(record.status === 'active' ? '禁用成功' : '启用成功');
        fetchData();
      }
    } catch (error) {
      message.error('操作失败');
      console.error(error);
    }
  };

  // ============== 表格列定义 ==============
  const columns = [
    {
      title: '序号',
      key: 'index',
      width: 80,
      render: (_, __, index) => (pagination.current - 1) * pagination.pageSize + index + 1,
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: 120,
    },
    {
      title: '真实姓名',
      dataIndex: 'real_name',
      key: 'real_name',
      width: 150,
    },
    {
      title: '角色',
      dataIndex: 'role_display',
      key: 'role',
      width: 150,
      render: (text, record) => (
        <Tag color={getRoleColor(record.role)}>{text}</Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status_display',
      key: 'status',
      width: 100,
      render: (text, record) => (
        <Tag color={record.status === 'active' ? 'success' : 'error'}>
          {text}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
    },
    {
      title: '操作',
      key: 'action',
      width: 280,
      fixed: 'right',
      render: (_, record) => (
        <Space>
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title={`确定要${record.status === 'active' ? '禁用' : '启用'}用户 ${record.username} 吗？`}
            onConfirm={() => handleToggleStatus(record)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              style={{ color: record.status === 'active' ? '#fa8c16' : '#52c41a' }}
              icon={record.status === 'active' ? <StopOutlined /> : <CheckCircleOutlined />}
            >
              {record.status === 'active' ? '禁用' : '启用'}
            </Button>
          </Popconfirm>
          <Popconfirm
            title={`确定要删除用户 ${record.username} 吗？`}
            description="删除后数据将无法恢复，请谨慎操作！"
            onConfirm={() => handleDelete(record)}
            okText="确定删除"
            cancelText="取消"
            okButtonProps={{ danger: true }}
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  // 角色颜色映射
  const getRoleColor = (role) => {
    const colorMap = {
      'data_consumer': 'blue',
      'requirement_manager': 'green',
      'operator': 'red',
      'project_manager': 'orange',
      'qa_manager': 'purple',
      'ops_manager': 'cyan',
      'team_lead': 'magenta',
      'admin': 'gold',
    };
    return colorMap[role] || 'default';
  };

  return (
    <div className="user-management-page">
      <Card title="用户管理" bordered={false}>
        {/* 搜索筛选区域 */}
        <Row gutter={16} className="search-area" align="middle">
          <Col span={5}>
            <Input
              placeholder="搜索用户名或姓名"
              value={searchParams.keyword}
              onChange={(e) => setSearchParams({ ...searchParams, keyword: e.target.value })}
              onPressEnter={handleSearch}
              prefix={<SearchOutlined />}
              allowClear
            />
          </Col>
          <Col span={4}>
            <Select
              placeholder="选择角色"
              value={searchParams.role}
              onChange={(value) => setSearchParams({ ...searchParams, role: value })}
              allowClear
              style={{ width: '100%' }}
            >
              {ROLE_OPTIONS.map(role => (
                <Option key={role.value} value={role.value}>{role.label}</Option>
              ))}
            </Select>
          </Col>
          <Col span={4}>
            <Select
              placeholder="选择状态"
              value={searchParams.status}
              onChange={(value) => setSearchParams({ ...searchParams, status: value })}
              allowClear
              style={{ width: '100%' }}
            >
              {STATUS_OPTIONS.map(status => (
                <Option key={status.value} value={status.value}>{status.label}</Option>
              ))}
            </Select>
          </Col>
          <Col span={5}>
            <Space>
              <Button type="primary" onClick={handleSearch} icon={<SearchOutlined />}>
                搜索
              </Button>
              <Button onClick={handleReset}>重置</Button>
            </Space>
          </Col>
          <Col span={6} style={{ textAlign: 'right' }}>
            <Button type="primary" icon={<PlusOutlined />} onClick={handleAdd}>
              新增用户
            </Button>
          </Col>
        </Row>

        {/* 表格区域 */}
        <Table
          columns={columns}
          dataSource={dataSource}
          rowKey="id"
          loading={loading}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
            pageSizeOptions: ['10', '20', '50'],
          }}
          onChange={handleTableChange}
          scroll={{ x: 1000 }}
        />
      </Card>

      {/* 新增/编辑弹窗 */}
      <UserForm
        visible={modalVisible}
        title={modalTitle}
        initialValues={editingUser}
        onCancel={handleModalClose}
        onSuccess={handleModalSuccess}
      />
    </div>
  );
}

export default UserManagement;
