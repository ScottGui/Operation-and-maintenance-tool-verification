/**
 * 服务管理页面
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
  Badge,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  ReloadOutlined,
  EyeOutlined,
  EditOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import { serviceApi } from '../../api';
import { SERVICE_STATUS, SERVICE_TYPE, SERVICE_LEVEL } from '../../utils/constants';
import './style.css';

const { Option } = Select;

const Service = () => {
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

  // 获取服务列表
  const fetchData = async (params = {}) => {
    try {
      setLoading(true);
      const res = await serviceApi.getList({
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
      console.error('获取服务列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
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

  // 获取状态标签
  const getStatusTag = (status) => {
    const config = SERVICE_STATUS[status?.toUpperCase()];
    if (!config) return <Tag>{status}</Tag>;
    return <Badge status={config.color} text={config.label} />;
  };

  // 获取类型标签
  const getTypeTag = (type) => {
    const config = Object.values(SERVICE_TYPE).find(
      (item) => item.value === type
    );
    return config?.label || type;
  };

  // 获取等级标签
  const getLevelTag = (level) => {
    const config = SERVICE_LEVEL[level?.toUpperCase()];
    if (!config) return <Tag>{level}</Tag>;
    return <Tag color={config.color}>{config.label}</Tag>;
  };

  // 查看详情
  const handleView = (record) => {
    setCurrentRecord(record);
    setDetailModalVisible(true);
  };

  // 删除服务
  const handleDelete = async (id) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个服务吗？此操作不可恢复。',
      onOk: async () => {
        try {
          await serviceApi.delete(id);
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
      title: '服务编号',
      dataIndex: 'service_no',
      key: 'service_no',
      width: 160,
    },
    {
      title: '服务名称',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: '类型',
      dataIndex: 'service_type',
      key: 'service_type',
      width: 120,
      render: getTypeTag,
    },
    {
      title: '等级',
      dataIndex: 'service_level',
      key: 'service_level',
      width: 130,
      render: getLevelTag,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: getStatusTag,
    },
    {
      title: '访问地址',
      dataIndex: 'access_url',
      key: 'access_url',
      width: 200,
      render: (text) => text ? (
        <a href={text} target="_blank" rel="noopener noreferrer">{text}</a>
      ) : '-',
    },
    {
      title: '负责人ID',
      dataIndex: 'owner_id',
      key: 'owner_id',
      width: 100,
      render: (text) => text || '-',
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
    <div className="service">
      <h2 className="page-title">服务管理</h2>
      
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
              placeholder="搜索服务编号/名称"
              prefix={<SearchOutlined />}
              allowClear
            />
          </Form.Item>
          
          <Form.Item name="status">
            <Select
              placeholder="选择状态"
              allowClear
              style={{ width: 120 }}
            >
              {Object.values(SERVICE_STATUS).map((item) => (
                <Option key={item.value} value={item.value}>
                  {item.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item name="service_type">
            <Select
              placeholder="选择类型"
              allowClear
              style={{ width: 120 }}
            >
              {Object.values(SERVICE_TYPE).map((item) => (
                <Option key={item.value} value={item.value}>
                  {item.label}
                </Option>
              ))}
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
          新建服务
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
        title="服务详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={720}
      >
        {currentRecord && (
          <div className="detail-content">
            <p><strong>服务编号：</strong>{currentRecord.service_no}</p>
            <p><strong>服务名称：</strong>{currentRecord.name}</p>
            <p><strong>类型：</strong>{getTypeTag(currentRecord.service_type)}</p>
            <p><strong>等级：</strong>{getLevelTag(currentRecord.service_level)}</p>
            <p><strong>状态：</strong>{getStatusTag(currentRecord.status)}</p>
            <p><strong>描述：</strong>{currentRecord.description || '-'}</p>
            <p><strong>访问地址：</strong>{currentRecord.access_url || '-'}</p>
            <p><strong>技术栈：</strong>{currentRecord.tech_stack || '-'}</p>
            <p><strong>负责人ID：</strong>{currentRecord.owner_id || '-'}</p>
            <p><strong>部署信息：</strong>{currentRecord.deployment_info || '-'}</p>
            <p><strong>备注：</strong>{currentRecord.remark || '-'}</p>
            <p><strong>创建时间：</strong>{currentRecord.created_at ? new Date(currentRecord.created_at).toLocaleString() : '-'}</p>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Service;
