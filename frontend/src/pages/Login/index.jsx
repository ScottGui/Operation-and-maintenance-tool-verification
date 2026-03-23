/**
 * 登录页面
 */
import { useState } from 'react';
import { Form, Input, Button, Card, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../../api';
import { tokenStorage, userStorage } from '../../utils/storage';
import './style.css';

const Login = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  // 处理登录
  const handleLogin = async (values) => {
    setLoading(true);
    try {
      const res = await authApi.login(values);
      const { access_token, token_type, expires_in } = res.data;
      
      // 保存 token
      tokenStorage.set(access_token);
      
      // 保存用户信息
      userStorage.set({
        username: values.username,
      });
      
      message.success('登录成功');
      navigate('/');
    } catch (error) {
      console.error('登录失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <Card className="login-card">
          <div className="login-header">
            <h1>公共数据运营授权运维平台</h1>
            <p>运维管理系统</p>
          </div>
          
          <Form
            name="login"
            onFinish={handleLogin}
            autoComplete="off"
            size="large"
          >
            <Form.Item
              name="username"
              rules={[{ required: true, message: '请输入用户名' }]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="用户名"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="密码"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={loading}
                block
              >
                登录
              </Button>
            </Form.Item>
          </Form>
          
          <div className="login-tips">
            <p>默认账号：admin / admin123</p>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Login;
