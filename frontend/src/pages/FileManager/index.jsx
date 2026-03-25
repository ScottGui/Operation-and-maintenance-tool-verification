/**
 * 文件管理中心页面
 * 
 * 功能：
 * - 文件上传（点击/拖拽）
 * - 文件列表展示
 * - 文件下载
 * - 文件删除
 * 
 * 作者/日期：AI / 2026-03-25
 */

import { useState, useEffect } from 'react';
import {
  Card,
  Upload,
  Button,
  List,
  Tag,
  message,
  Popconfirm,
  Empty,
  Spin,
} from 'antd';
import {
  UploadOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FileExcelOutlined,
  FileImageOutlined,
  FileOutlined,
  DownloadOutlined,
  DeleteOutlined,
  InboxOutlined,
} from '@ant-design/icons';
import { fileApi, getFileTypeConfig } from '../../api/file';
import './style.css';

const { Dragger } = Upload;

const FileManager = () => {
  const [fileList, setFileList] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  // 加载文件列表
  const loadFiles = async () => {
    setLoading(true);
    try {
      const res = await fileApi.getList();
      if (res.data?.code === 200) {
        setFileList(res.data.data);
      }
    } catch (error) {
      message.error('加载文件列表失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFiles();
  }, []);

  // 上传配置
  const uploadProps = {
    name: 'file',
    multiple: true,
    customRequest: async ({ file, onSuccess, onError, onProgress }) => {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);

      try {
        const res = await fileApi.upload(formData);
        if (res.data?.code === 200) {
          message.success(`${file.name} 上传成功`);
          onSuccess?.(res.data.data);
          loadFiles(); // 刷新列表
        } else {
          onError?.(new Error(res.data?.message));
        }
      } catch (error) {
        message.error(`${file.name} 上传失败: ${error.response?.data?.detail || '未知错误'}`);
        onError?.(error);
      } finally {
        setUploading(false);
      }
    },
    onChange: (info) => {
      // 上传状态变化回调
    },
    showUploadList: false, // 使用自定义列表
  };

  // 下载文件
  const handleDownload = (file) => {
    const url = fileApi.getDownloadUrl(file.id);
    // 创建一个临时的a标签下载
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', file.file_name);
    link.setAttribute('target', '_blank');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 删除文件
  const handleDelete = async (fileId) => {
    try {
      const res = await fileApi.delete(fileId);
      if (res.data?.code === 200) {
        message.success('删除成功');
        loadFiles();
      }
    } catch (error) {
      message.error(error.response?.data?.detail || '删除失败');
    }
  };

  // 获取文件图标
  const getFileIcon = (fileType) => {
    const config = getFileTypeConfig(fileType);
    const iconStyle = { fontSize: 24, color: config.color };
    
    switch (config.icon) {
      case 'file-pdf':
        return <FilePdfOutlined style={iconStyle} />;
      case 'file-word':
        return <FileWordOutlined style={iconStyle} />;
      case 'file-excel':
        return <FileExcelOutlined style={iconStyle} />;
      case 'file-image':
        return <FileImageOutlined style={iconStyle} />;
      default:
        return <FileOutlined style={iconStyle} />;
    }
  };

  return (
    <div className="file-manager-page">
      <div className="page-header">
        <h2>文档管理中心</h2>
      </div>
      
      <Card bordered={false} className="upload-card">
        {/* 上传区域 */}
        <Dragger {...uploadProps} className="upload-dragger">
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">点击或拖拽文件到此处上传</p>
          <p className="ant-upload-hint">
            支持 PDF、Word、Excel、图片格式，单个文件不超过50MB
          </p>
        </Dragger>

        {/* 文件列表 */}
        <div className="file-list-section">
          <h3>文件列表</h3>
          <Spin spinning={loading || uploading}>
            {fileList.length > 0 ? (
              <List
                className="file-list"
                itemLayout="horizontal"
                dataSource={fileList}
                renderItem={(item) => (
                  <List.Item
                    actions={[
                      <Button
                        type="link"
                        icon={<DownloadOutlined />}
                        onClick={() => handleDownload(item)}
                      >
                        下载
                      </Button>,
                      <Popconfirm
                        title="确定要删除该文件吗？"
                        onConfirm={() => handleDelete(item.id)}
                        okText="确定"
                        cancelText="取消"
                      >
                        <Button type="link" danger icon={<DeleteOutlined />}>
                          删除
                        </Button>
                      </Popconfirm>,
                    ]}
                  >
                    <List.Item.Meta
                      avatar={getFileIcon(item.file_type)}
                      title={item.file_name}
                      description={
                        <span>
                          <Tag>{item.file_size_display}</Tag>
                          <Tag color="blue">{getFileTypeConfig(item.file_type).label}</Tag>
                          <span className="upload-time">{item.uploaded_at}</span>
                        </span>
                      }
                    />
                  </List.Item>
                )}
              />
            ) : (
              <Empty description="暂无文档" />
            )}
          </Spin>
        </div>
      </Card>
    </div>
  );
};

export default FileManager;
