/**
 * 资产管理页面
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
import { assetApi } from '../../api';
import { ASSET_STATUS, ASSET_TYPE } from '../../utils/constants';
import './style.css';

const { Option } = Select;

const Asset = () => {
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

  // 获取资产列表
  const fetchData = async (params = {}) => {
    try {
      setLoading(true);
      const res = await assetApi.getList({
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
      console.error('获取资产列表失败:', error);
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
    const config = ASSET_STATUS[status?.toUpperCase()];
    if (!config) return <Tag>{status}</Tag>;
    return <Badge status={config.color} text={config.label} />;
  };

  // 获取类型标签
  const getTypeTag = (type) => {
    const config = Object.values(ASSET_TYPE).find(
      (item) => item.value === type
    );
    return config?.label || type;
  };

  // 查看详情
  const handleView = (record) => {
    setCurrentRecord(record);
    setDetailModalVisible(true);
  };

  // 删除资产
  const handleDelete = async (id) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个资产吗？此操作不可恢复。',
      onOk: async () => {
        try {
          await assetApi.delete(id);
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
      title: '资产编号',
      dataIndex: 'asset_no',
      key: 'asset_no',
      width: 160,
    },
    {
      title: '资产名称',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: '类型',
      dataIndex: 'asset_type',
      key: 'asset_type',
      width: 120,
      render: getTypeTag,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: getStatusTag,
    },
    {
      title: '厂商',
      dataIndex: 'vendor',
      key: 'vendor',
      width: 140,
      render: (text) => text || '-',
    },
    {
      title: '型号',
      dataIndex: 'model',
      key: 'model',
      width: 140,
      render: (text) => text || '-',
    },
    {
      title: 'IP地址',
      dataIndex: 'ip_address',
      key: 'ip_address',
      width: 140,
      render: (text) => text || '-',
    },
    {
      title: '位置',
      dataIndex: 'location',
      key: 'location',
      width: 160,
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
    <div className="asset">
      <h2 className="page-title">资产管理</h2>
      
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
              placeholder="搜索资产编号/名称"
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
              {Object.values(ASSET_STATUS).map((item) => (
                <Option key={item.value} value={item.value}>
                  {item.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item name="asset_type">
            <Select
              placeholder="选择类型"
              allowClear
              style={{ width: 120 }}
            >
              {Object.values(ASSET_TYPE).map((item) => (
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
          新建资产
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
        title="资产详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={720}
      >
        {currentRecord && (
          <div className="detail-content">
            <p><strong>资产编号：</strong>{currentRecord.asset_no}</p>
            <p><strong>资产名称：</strong>{currentRecord.name}</p>
            <p><strong>类型：</strong>{getTypeTag(currentRecord.asset_type)}</p>
            <p><strong>状态：</strong>{getStatusTag(currentRecord.status)}</p>
            <p><strong>厂商：</strong>{currentRecord.vendor || '-'}</p>
            <p><strong>型号：</strong>{currentRecord.model || '-'}</p>
            <p><strong>序列号：</strong>{currentRecord.serial_number || '-'}</p>
            <p><strong>IP地址：</strong>{currentRecord.ip_address || '-'}</p>
            <p><strong>位置：</strong>{currentRecord.location || '-'}</p>
            <p><strong>配置信息：</strong>{currentRecord.configuration || '-'}</p>
            <p><strong>备注：</strong>{currentRecord.remark || '-'}</p>
            <p><strong>创建时间：</strong>{currentRecord.created_at ? new Date(currentRecord.created_at).toLocaleString() : '-'}</p>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Asset;
