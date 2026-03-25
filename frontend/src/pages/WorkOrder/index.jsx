/**
 * 需求单管理页面
 */
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
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
  DatePicker,
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
import { useNavigate } from 'react-router-dom';
import { workOrderApi } from '../../api';
import {
  WORK_ORDER_STATUS,
  WORK_ORDER_PRIORITY,
  WORK_ORDER_TYPE,
} from '../../utils/constants';
import './style.css';

const { RangePicker } = DatePicker;
const { Option } = Select;

const WorkOrder = () => {
  const navigate = useNavigate();
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
  const [searchParams] = useSearchParams();

  // 获取需求单列表
  const fetchData = async (params = {}) => {
    try {
      setLoading(true);
      const res = await workOrderApi.getList({
        page: pagination.current,
        page_size: pagination.pageSize,
        ...params,
      });
      setData(res.data.data?.items || res.data.items || []);
      setPagination({
        ...pagination,
        total: res.data.data?.total || res.data.total || 0,
      });
    } catch (error) {
      console.error('获取需求单列表失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // 读取 URL 参数并设置筛选条件
    const status = searchParams.get('status');
    const initialParams = {};
    if (status) {
      initialParams.status = status;
      searchForm.setFieldsValue({ status });
    }
    fetchData(initialParams);
  }, [searchParams]);

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
  const getStatusTag = (status, record) => {
    // 优先使用后端返回的 status_display
    if (record?.status_display) {
      // 根据状态值获取颜色
      const statusKey = Object.keys(WORK_ORDER_STATUS).find(
        key => WORK_ORDER_STATUS[key].value === status
      );
      const color = statusKey ? WORK_ORDER_STATUS[statusKey].color : 'default';
      return <Badge status={color} text={record.status_display} />;
    }
    // 兜底：通过状态值查找
    const config = Object.values(WORK_ORDER_STATUS).find(
      (item) => item.value === status
    );
    if (!config) return <Tag>{status}</Tag>;
    return <Badge status={config.color} text={config.label} />;
  };

  // 获取优先级标签
  const getPriorityTag = (priority) => {
    const config = WORK_ORDER_PRIORITY[priority?.toUpperCase()];
    if (!config) return <Tag>{priority}</Tag>;
    return <Tag color={config.color}>{config.label}</Tag>;
  };

  // 获取类型标签
  const getTypeTag = (type) => {
    const config = Object.values(WORK_ORDER_TYPE).find(
      (item) => item.value === type
    );
    return config?.label || type;
  };

  // 查看详情
  const handleView = (record) => {
    setCurrentRecord(record);
    setDetailModalVisible(true);
  };

  // 删除需求单
  const handleDelete = async (id) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个需求单吗？此操作不可恢复。',
      onOk: async () => {
        try {
          await workOrderApi.delete(id);
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
      title: '需求单号',
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
      title: '类型',
      dataIndex: 'type',
      key: 'type',
      width: 120,
      render: (type, record) => record?.type_display || getTypeTag(type),
    },
    {
      title: '优先级',
      dataIndex: 'priority',
      key: 'priority',
      width: 100,
      render: getPriorityTag,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status, record) => getStatusTag(status, record),
    },
    {
      title: '创建人',
      dataIndex: 'creator_role',
      key: 'creator_role',
      width: 120,
      render: (role) => {
        const roleMap = {
          'data_consumer': '用数方',
          'requirement_manager': '需求经理',
          'operator': '运营方',
          'project_manager': '项目经理',
          'qa_manager': '质量稽核经理',
          'ops_manager': '数据运维经理',
          'team_lead': '四方组长',
          'admin': '管理员',
        };
        return roleMap[role] || role;
      },
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
    <div className="work-order">
      <h2 className="page-title">需求单管理</h2>
      
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
              placeholder="搜索需求单号/标题"
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
              {Object.values(WORK_ORDER_STATUS).map((item) => (
                <Option key={item.value} value={item.value}>
                  {item.label}
                </Option>
              ))}
            </Select>
          </Form.Item>
          
          <Form.Item name="type">
            <Select
              placeholder="选择类型"
              allowClear
              style={{ width: 120 }}
            >
              {Object.values(WORK_ORDER_TYPE).map((item) => (
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
        <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/work-orders/create')}>
          新建需求单
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
          scroll={{ x: 1200 }}
        />
      </Card>

      {/* 详情弹窗 */}
      <Modal
        title="需求单详情"
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={null}
        width={720}
      >
        {currentRecord && (
          <div className="detail-content">
            <p><strong>需求单号：</strong>{currentRecord.order_no}</p>
            <p><strong>标题：</strong>{currentRecord.title}</p>
            <p><strong>类型：</strong>{currentRecord.type_display || getTypeTag(currentRecord.type)}</p>
            <p><strong>使用频率：</strong>{currentRecord.frequency_display || '-'}</p>
            <p><strong>状态：</strong>{getStatusTag(currentRecord.status, currentRecord)}</p>
            <p><strong>期望完成时间：</strong>{currentRecord.expected_date || '-'}</p>
            <p><strong>创建时间：</strong>{currentRecord.created_at ? new Date(currentRecord.created_at).toLocaleString() : '-'}</p>
            <p><strong>业务背景：</strong>{currentRecord.business_background || '-'}</p>
            <p><strong>数据范围：</strong>{currentRecord.data_scope || '-'}</p>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default WorkOrder;
