/**
 * 路由配置
 */
import { createBrowserRouter, Navigate } from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import Login from '../pages/Login';
import Dashboard from '../pages/Dashboard';
import WorkOrder from '../pages/WorkOrder';
import Asset from '../pages/Asset';
import Service from '../pages/Service';
import User from '../pages/User';
import { tokenStorage } from '../utils/storage';

// 路由守卫组件
const PrivateRoute = ({ children }) => {
  const token = tokenStorage.get();
  return token ? children : <Navigate to="/login" replace />;
};

// 公开路由守卫
const PublicRoute = ({ children }) => {
  const token = tokenStorage.get();
  return !token ? children : <Navigate to="/" replace />;
};

const router = createBrowserRouter([
  {
    path: '/login',
    element: (
      <PublicRoute>
        <Login />
      </PublicRoute>
    ),
  },
  {
    path: '/',
    element: (
      <PrivateRoute>
        <MainLayout />
      </PrivateRoute>
    ),
    children: [
      {
        index: true,
        element: <Dashboard />,
      },
      {
        path: 'work-orders',
        element: <WorkOrder />,
      },
      {
        path: 'assets',
        element: <Asset />,
      },
      {
        path: 'services',
        element: <Service />,
      },
      {
        path: 'users',
        element: <User />,
      },
    ],
  },
]);

export default router;
