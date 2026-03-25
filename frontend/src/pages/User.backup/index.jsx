/**
 * 用户管理页面
 */
import { useState, useEffect } from 'react';
import {
  Table,
  Button,
  Card,
  Form,
  Input,
  Select,
  Tag,
  Space,
  Modal,
  message,
  Switch,
  Avatar,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { userApi } from '../../api';
import './style.css';

const { Option } = Select;

const User = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  });
  const [searchForm] = Form.useForm();
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [currentRecord, setCurrentRecord] = useState(null);
  const [departments, setDepartments] = useState([]);
  const [roles, setRoles] = useState([]);

  // 获取用户列表
  const fetchData = async (params = {}) => {
    try {
      setLoading(true);
      const res = await userApi.getList({
        page: pagination.current,
        page_size: pagination.pageSize,
        ...params,
      });
      setData(res.data.list);
      setPagination({
        ...pagination,
        total: res.data.pagination.total,
      });
    } catch (error) {
      console.error('获取用户列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 获取部门和角色数据
  const fetchMetaData = async () => {
    try {
      const [deptRes, roleRes] = await Promise.all([
        userApi.getDepartments(),
        userApi.getRoles(),
      ]);
      setDepartments(deptRes.data || []);
      setRoles(roleRes.data || []);
    } catch (error) {
      console.error('获取元数据失败:', error);
    }
  };

  useEffect(() => {
    fetchData();
    fetchMetaData();
  }, []);

  // 处理搜索
  const handleSearch = (values) => {
    fetchData(values);
  };

  // 处理重置
  const handleReset = () => {
    searchForm.resetFields();
    fetchData();
  };

  // 查看详情
  const handleView = (record) => {
    setCurrentRecord(record);
    setDetailModalVisible(true);
  };

  // 删除用户
  const handleDelete = async (id) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个用户吗？此操作不可恢复。',
      onOk: async () => {
        try {
          await userApi.delete(id);
          message.success('删除成功');
          fetchData();
        } catch (error) {
          console.error('删除失败:', error);
        }
      },
    });
  };

  // 表格列定义
  const columns = [
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: 120,
    },
    {
      title: '姓名',
      dataIndex: 'real_name',
      key: 'real_name',
      width: 120,
      render: (text) => text || '-',
    },
    {
      title: '头像',
      dataIndex: 'avatar',
      key: 'avatar',
      width: 80,
      render: (text) => (
        <Avatar 
          src={text} 
          icon={!text && <UserOutlined />}
          size="small"
        />
      ),
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 180,
      render: (text) => text || '-',
    },
    {
      title: '电话',
      dataIndex: 'phone',
      key: 'phone',
      width: 120,
      render: (text) => text || '-',
    },
    {
      title: '部门',
      dataIndex: 'department_name',
      key: 'department_name',
      width: 120,
      render: (text) => text || '-',
    },
    {
      title: '角色',
      dataIndex: 'roles',
      key: 'roles',
      width: 150,
      render: (roles) => (
        <Space size="small" wrap>
          {roles?.map((role) => (
            <Tag key={role.id} color="blue">{role.name}</Tag>
          ))}
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive) => (
        <Tag color={isActive ? 'success' : 'error'}>
          {isActive ? '启用' : '禁用'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text) => text ? new Date(text).toLocaleString() : '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 180,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleView(record)}
          >
            查看
          </Button>
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            danger
            icon={<DeleteOutlined />}
            onClick={() => handleDelete(record.id)}
          >
            删除
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div className="user">
      <h2 className="page-title">用户管理</h2>
      
      {/* 搜索表单 */}
      <Card className="search-card">
        <Form
          form={searchForm}
          layout="inline"
          onFinish={handleSearch}
          className="search-form"
        >
          <Form.Item name="keyword">
            <Input
              placeholder="搜索用户名/姓名/邮箱"
              prefix={<SearchOutlined />}
              allowClear
            />
          </Form.Item>
          
          <Form.Item name="department_id">
            <Select
              placeholder="选择部门"
              allowClear
              style={{ width: 140 }}
            >
              {departments.map((dept) => (
                <Option key={dept.id} value={dept.id}>
                  {dept.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item name="is_active">
            <Select
              placeholder="选择状态"
              allowClear
              style={{ width: 120 }}
            >
              <Option value={true}>启用</Option>
              <Option value={false}>禁用</Option>
            </Select>
          </Form.Item>
          
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" icon={<SearchOutlined />}>
                搜索
              </Button>
              <Button icon={<ReloadOutlined />} onClick={handleReset}>
                重置
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>

      {/* 操作栏 */}
      <div className="table-operations">
        <Button type="primary" icon={<PlusOutlined />}>
          新建用户
        </Button>
      </div>

      {/* 表格 */}
      <Card>
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
          onChange={(newPagination) => {
            setPagination(newPagination);
            fetchData({
              page: newPagination.current,
              page_size: newPagination.pageSize,
            });
          }}
          scroll={{ x: 1300 }}
        />
      </Card>

      {/* 详情弹窗 */}
      <Modal
        title="用户详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={600}
      >
        {currentRecord && (
          <div className="detail-content">
            <div className="user-avatar-section">
              <Avatar 
                src={currentRecord.avatar} 
                icon={!currentRecord.avatar && <UserOutlined />}
                size={80}
              />
              <div className="user-basic-info">
                <p><strong>用户名：</strong>{currentRecord.username}</p>
                <p><strong>姓名：</strong>{currentRecord.real_name || '-'}</p>
              </div>
            </div>
            <p><strong>邮箱：</strong>{currentRecord.email || '-'}</p>
            <p><strong>电话：</strong>{currentRecord.phone || '-'}</p>
            <p><strong>部门：</strong>{currentRecord.department_name || '-'}</p>
            <p><strong>角色：</strong>
              {currentRecord.roles?.map((role) => (
                <Tag key={role.id} color="blue">{role.name}</Tag>
              ))}
            </p>
            <p><strong>状态：</strong>
              <Tag color={currentRecord.is_active ? 'success' : 'error'}>
                {currentRecord.is_active ? '启用' : '禁用'}
              </Tag>
            </p>
            <p><strong>最后登录：</strong>{currentRecord.last_login_at ? new Date(currentRecord.last_login_at).toLocaleString() : '-'}</p>
            <p><strong>创建时间：</strong>{currentRecord.created_at ? new Date(currentRecord.created_at).toLocaleString() : '-'}</p>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default User;
