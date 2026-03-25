/**
 * 用户表单弹窗组件
 * 
 * 功能：
 * - 新增用户表单
 * - 编辑用户表单
 * - 表单校验（用户名、密码、角色等）
 * 
 * 作者/日期：AI / 2026-03-24
 */

import React, { useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  Select,
  Switch,
  message,
} from 'antd';
import { userApi, ROLE_OPTIONS } from '../../api/user';

const { Option } = Select;

function UserForm({ visible, title, initialValues, onCancel, onSuccess }) {
  const [form] = Form.useForm();
  const isEdit = !!initialValues;

  // 当initialValues变化时，重置表单
  useEffect(() => {
    if (visible) {
      if (initialValues) {
        // 编辑模式：回填数据（不包含密码）
        form.setFieldsValue({
          username: initialValues.username,
          real_name: initialValues.real_name,
          role: initialValues.role,
          status: initialValues.status === 'active',
        });
      } else {
        // 新增模式：重置表单
        form.resetFields();
      }
    }
  }, [visible, initialValues, form]);

  // 提交表单
  const handleSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      // 处理status（Switch返回boolean，转换为字符串）
      const submitData = {
        ...values,
        status: values.status ? 'active' : 'inactive',
      };
      
      // 编辑模式下，如果没有填写密码，不传password字段
      if (isEdit && !submitData.password) {
        delete submitData.password;
      }
      
      // 调用API
      let response;
      if (isEdit) {
        response = await userApi.update(initialValues.id, submitData);
      } else {
        response = await userApi.create(submitData);
      }
      
      if (response.data?.code === 200) {
        message.success(isEdit ? '更新成功' : '创建成功');
        onSuccess();
      } else {
        message.error(response.data?.message || '操作失败');
      }
    } catch (error) {
      if (error.response?.data?.message) {
        message.error(error.response.data.message);
      } else if (error.errorFields) {
        // 表单校验错误，不提示
        return;
      } else {
        message.error('操作失败');
      }
      console.error(error);
    }
  };

  return (
    <Modal
      title={title}
      open={visible}
      onOk={handleSubmit}
      onCancel={onCancel}
      width={600}
      okText="保存"
      cancelText="取消"
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        initialValues={{
          status: true, // 默认启用
        }}
      >
        {/* 用户名 */}
        <Form.Item
          label="用户名"
          name="username"
          rules={[
            { required: true, message: '请输入用户名' },
            { min: 4, message: '用户名至少4位' },
            { max: 20, message: '用户名最多20位' },
            { pattern: /^[a-zA-Z0-9]+$/, message: '用户名只能包含字母和数字' },
          ]}
        >
          <Input 
            placeholder="请输入用户名，字母数字，4-20位" 
            disabled={isEdit} // 编辑模式下用户名不可修改
          />
        </Form.Item>

        {/* 真实姓名 */}
        <Form.Item
          label="真实姓名"
          name="real_name"
          rules={[
            { required: true, message: '请输入真实姓名' },
            { min: 2, message: '姓名至少2个字' },
            { max: 20, message: '姓名最多20个字' },
            { pattern: /^[\u4e00-\u9fa5]+$/, message: '姓名只能包含中文' },
          ]}
        >
          <Input placeholder="请输入真实姓名，2-20个中文字符" />
        </Form.Item>

        {/* 密码 */}
        <Form.Item
          label={isEdit ? "密码（留空则不修改）" : "密码"}
          name="password"
          rules={[
            { required: !isEdit, message: '请输入密码' },
            { min: 6, message: '密码至少6位' },
            { max: 20, message: '密码最多20位' },
          ]}
        >
          <Input.Password placeholder={isEdit ? "不填则保持原密码" : "请输入密码，6-20位"} />
        </Form.Item>

        {/* 角色 */}
        <Form.Item
          label="角色"
          name="role"
          rules={[{ required: true, message: '请选择角色' }]}
        >
          <Select placeholder="请选择角色">
            {ROLE_OPTIONS.map(role => (
              <Option key={role.value} value={role.value}>{role.label}</Option>
            ))}
          </Select>
        </Form.Item>

        {/* 账号状态 */}
        <Form.Item
          label="账号状态"
          name="status"
          valuePropName="checked"
        >
          <Switch 
            checkedChildren="启用" 
            unCheckedChildren="禁用"
          />
        </Form.Item>
      </Form>
    </Modal>
  );
}

export default UserForm;
