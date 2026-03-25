/**
 * 用数需求发起页面
 * 
 * 功能：
 * - 创建新的用数需求
 * - 支持保存草稿和提交审批
 * - 仅用数方(data_consumer)角色可访问
 * 
 * 作者/日期：AI / 2026-03-25
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Form,
  Input,
  Select,
  DatePicker,
  Button,
  Upload,
  message,
  Alert,
  Space,
} from 'antd';
import {
  SaveOutlined,
  SendOutlined,
  UploadOutlined,
  InboxOutlined,
} from '@ant-design/icons';
import { userStorage } from '../../utils/storage';
import { workOrderApi } from '../../api';
import { fileApi } from '../../api/file';
import './style.css';

const { TextArea } = Input;
const { Option } = Select;
const { Dragger } = Upload;

// 需求类型选项
const REQUIREMENT_TYPE_OPTIONS = [
  { value: 'api_development', label: '接口开发' },
  { value: 'data_export', label: '数据导出' },
  { value: 'data_sync', label: '数据同步' },
  { value: 'other', label: '其他' },
];

// 使用频率选项
const FREQUENCY_OPTIONS = [
  { value: 'realtime', label: '实时' },
  { value: 'daily', label: '每日' },
  { value: 'weekly', label: '每周' },
  { value: 'monthly', label: '每月' },
  { value: 'once', label: '一次性' },
];

const WorkOrderCreate = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [fileList, setFileList] = useState([]);
  const [userInfo, setUserInfo] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  // 检查用户权限
  useEffect(() => {
    const user = userStorage.get();
    if (!user) {
      message.error('请先登录');
      navigate('/login');
      return;
    }
    
    if (user.role !== 'data_consumer') {
      message.error('只有用数方可以发起需求');
      navigate('/');
      return;
    }
    
    setUserInfo(user);
  }, [navigate]);

  // 表单提交
  const handleSubmit = async (status) => {
    try {
      const values = await form.validateFields();
      setLoading(true);

      // 构建提交数据
      const submitData = {
        title: values.title,
        type: values.type,
        frequency: values.frequency,
        expected_date: values.expected_date.format('YYYY-MM-DD'),
        business_background: values.business_background,
        data_scope: values.data_scope,
        is_draft: status === 'draft',
        file_ids: uploadedFiles.map(file => file.id),
      };

      // 调用创建API
      const response = await workOrderApi.create(submitData);

      if (response.data?.code === 200) {
        message.success(status === 'draft' ? '草稿保存成功' : '需求提交成功');
        // 提交成功后跳转到需求管理池列表页
        navigate('/work-orders');
      } else {
        message.error(response.data?.message || '操作失败');
      }
    } catch (error) {
      if (error.errorFields) {
        // 表单校验错误，不提示
        return;
      }
      message.error(error.response?.data?.message || '操作失败');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // 保存草稿
  const handleSaveDraft = () => {
    handleSubmit('draft');
  };

  // 提交审批
  const handleSubmitApproval = () => {
    handleSubmit('pending_review');
  };

  // 文件上传配置
  const uploadProps = {
    name: 'file',
    multiple: true,
    fileList,
    customRequest: async ({ file, onSuccess, onError }) => {
      const formData = new FormData();
      formData.append('file', file);

      try {
        const res = await fileApi.upload(formData);
        if (res.data?.code === 200) {
          message.success(`${file.name} 上传成功`);
          setUploadedFiles(prev => [...prev, res.data.data]);
          onSuccess?.(res.data.data);
        } else {
          onError?.(new Error(res.data?.message));
        }
      } catch (error) {
        message.error(`${file.name} 上传失败`);
        onError?.(error);
      }
    },
    onChange: ({ fileList: newFileList }) => {
      setFileList(newFileList);
    },
    onRemove: async (file) => {
      // 如果文件已上传，从服务器删除
      const uploadedFile = uploadedFiles.find(f => f.file_name === file.name);
      if (uploadedFile) {
        try {
          await fileApi.delete(uploadedFile.id);
          setUploadedFiles(prev => prev.filter(f => f.id !== uploadedFile.id));
          message.success('文件删除成功');
        } catch (error) {
          message.error('文件删除失败');
        }
      }
    },
  };

  // 如果不是用数方，显示无权限提示
  if (!userInfo || userInfo.role !== 'data_consumer') {
    return (
      <div className="work-order-create">
        <Alert
          message="无权限访问"
          description="只有用数方角色可以发起需求"
          type="warning"
          showIcon
        />
      </div>
    );
  }

  return (
    <div className="work-order-create">
      <h2 className="page-title">用数需求发起</h2>
      
      <Card bordered={false} className="form-card">
        <Form
          form={form}
          layout="vertical"
          className="requirement-form"
        >
          {/* 需求标题 */}
          <Form.Item
            label="需求标题"
            name="title"
            rules={[
              { required: true, message: '请输入需求标题' },
              { max: 100, message: '标题最多100个字符' },
            ]}
          >
            <Input 
              placeholder="请输入需求标题" 
              maxLength={100}
              showCount
            />
          </Form.Item>

          {/* 需求类型 */}
          <Form.Item
            label="需求类型"
            name="type"
            rules={[{ required: true, message: '请选择需求类型' }]}
          >
            <Select placeholder="请选择需求类型">
              {REQUIREMENT_TYPE_OPTIONS.map(option => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          {/* 使用频率 */}
          <Form.Item
            label="使用频率"
            name="frequency"
            rules={[{ required: true, message: '请选择使用频率' }]}
          >
            <Select placeholder="请选择使用频率">
              {FREQUENCY_OPTIONS.map(option => (
                <Option key={option.value} value={option.value}>
                  {option.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          {/* 期望完成时间 */}
          <Form.Item
            label="期望完成时间"
            name="expected_date"
            rules={[{ required: true, message: '请选择期望完成时间' }]}
          >
            <DatePicker 
              style={{ width: '100%' }}
              placeholder="请选择期望完成时间"
              format="YYYY-MM-DD"
              disabledDate={(current) => {
                // 不能选择过去的日期
                return current && current < new Date().setHours(0, 0, 0, 0);
              }}
            />
          </Form.Item>

          {/* 业务背景 */}
          <Form.Item
            label="业务背景"
            name="business_background"
            rules={[
              { required: true, message: '请输入业务背景' },
              { max: 2000, message: '业务背景最多2000个字符' },
            ]}
          >
            <TextArea 
              placeholder="请描述业务背景，包括业务场景、目的等信息"
              rows={4}
              maxLength={2000}
              showCount
            />
          </Form.Item>

          {/* 数据范围 */}
          <Form.Item
            label="数据范围"
            name="data_scope"
            rules={[
              { required: true, message: '请输入数据范围' },
              { max: 2000, message: '数据范围最多2000个字符' },
            ]}
          >
            <TextArea 
              placeholder="请描述所需数据的范围，包括数据来源、数据字段、筛选条件等"
              rows={4}
              maxLength={2000}
              showCount
            />
          </Form.Item>

          {/* 附件上传 */}
          <Form.Item
            label="需求依据证明"
            name="attachments"
            extra="支持 PDF、Word、Excel、图片格式，单个文件不超过50MB，请上传需求依据相关材料"
          >
            <Dragger {...uploadProps} className="upload-dragger">
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此处上传</p>
              <p className="ant-upload-hint">
                请上传需求依据相关材料，如业务审批单、需求文档等
              </p>
            </Dragger>
          </Form.Item>

          {/* 底部按钮 */}
          <Form.Item className="form-actions">
            <Space size="middle">
              <Button
                size="large"
                icon={<SaveOutlined />}
                onClick={handleSaveDraft}
                loading={loading}
              >
                保存草稿
              </Button>
              <Button
                type="primary"
                size="large"
                icon={<SendOutlined />}
                onClick={handleSubmitApproval}
                loading={loading}
              >
                提交审批
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default WorkOrderCreate;
