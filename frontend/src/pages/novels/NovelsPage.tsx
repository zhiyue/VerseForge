import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Form,
  Input,
  InputNumber,
  Select,
  Progress,
  Tooltip,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

import { useNovels } from '@/hooks/useNovels';
import type { Novel } from '@/types';
import { formatDateTime } from '@/utils/date';

const { Option } = Select;

const NovelsPage: React.FC = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [selectedNovel, setSelectedNovel] = useState<Novel | null>(null);
  const [deleteConfirmVisible, setDeleteConfirmVisible] = useState(false);

  const {
    novels,
    isLoading,
    createNovel,
    updateNovel,
    deleteNovel,
    startGeneration,
    pauseGeneration,
  } = useNovels();

  const handleCreate = async (values: any) => {
    await createNovel(values);
    setIsModalVisible(false);
    form.resetFields();
  };

  const handleDelete = async () => {
    if (selectedNovel) {
      await deleteNovel(selectedNovel.id);
      setDeleteConfirmVisible(false);
      setSelectedNovel(null);
    }
  };

  const handleGeneration = async (novel: Novel) => {
    if (novel.status === 'generating') {
      await pauseGeneration(novel.id);
    } else {
      await startGeneration(novel.id);
    }
  };

  const columns: ColumnsType<Novel> = [
    {
      title: '标题',
      dataIndex: 'title',
      key: 'title',
      render: (text, record) => (
        <a onClick={() => navigate(`/novels/${record.id}`)}>{text}</a>
      ),
    },
    {
      title: '类型',
      dataIndex: 'genre',
      key: 'genre',
      render: (text) => <Tag>{text || '未分类'}</Tag>,
    },
    {
      title: '字数',
      key: 'word_count',
      render: (_, record) => (
        <Space direction="vertical" style={{ width: '100%' }}>
          <span>
            {record.current_word_count} / {record.target_word_count} 字
          </span>
          <Progress
            percent={Math.round(
              (record.current_word_count / record.target_word_count) * 100
            )}
            size="small"
            status={record.status === 'completed' ? 'success' : 'active'}
          />
        </Space>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const statusMap: Record<string, { color: string; text: string }> = {
          draft: { color: 'default', text: '草稿' },
          generating: { color: 'processing', text: '生成中' },
          paused: { color: 'warning', text: '已暂停' },
          completed: { color: 'success', text: '已完成' },
          error: { color: 'error', text: '错误' },
        };
        const { color, text } = statusMap[status] || {
          color: 'default',
          text: status,
        };
        return <Tag color={color}>{text}</Tag>;
      },
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (text) => formatDateTime(text),
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Tooltip title="编辑">
            <Button
              type="text"
              icon={<EditOutlined />}
              onClick={() => navigate(`/novels/${record.id}/edit`)}
            />
          </Tooltip>
          {record.status !== 'completed' && (
            <Tooltip
              title={record.status === 'generating' ? '暂停生成' : '开始生成'}
            >
              <Button
                type="text"
                icon={
                  record.status === 'generating' ? (
                    <PauseCircleOutlined />
                  ) : (
                    <PlayCircleOutlined />
                  )
                }
                onClick={() => handleGeneration(record)}
              />
            </Tooltip>
          )}
          <Tooltip title="删除">
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              onClick={() => {
                setSelectedNovel(record);
                setDeleteConfirmVisible(true);
              }}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  return (
    <>
      <Card
        title="小说管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setIsModalVisible(true)}
          >
            创建小说
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={novels}
          loading={isLoading}
          rowKey="id"
          pagination={{
            showQuickJumper: true,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>

      {/* 创建/编辑表单 */}
      <Modal
        title={selectedNovel ? '编辑小说' : '创建小说'}
        open={isModalVisible}
        onOk={() => form.submit()}
        onCancel={() => {
          setIsModalVisible(false);
          setSelectedNovel(null);
          form.resetFields();
        }}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
          initialValues={selectedNovel || {}}
        >
          <Form.Item
            name="title"
            label="标题"
            rules={[{ required: true, message: '请输入小说标题' }]}
          >
            <Input />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input.TextArea rows={4} />
          </Form.Item>
          <Form.Item name="genre" label="类型">
            <Select>
              <Option value="玄幻">玄幻</Option>
              <Option value="修仙">修仙</Option>
              <Option value="都市">都市</Option>
              <Option value="科幻">科幻</Option>
              <Option value="历史">历史</Option>
            </Select>
          </Form.Item>
          <Form.Item
            name="target_word_count"
            label="目标字数"
            rules={[{ required: true, message: '请输入目标字数' }]}
          >
            <InputNumber min={1000} step={1000} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>

      {/* 删除确认框 */}
      <Modal
        title="确认删除"
        open={deleteConfirmVisible}
        onOk={handleDelete}
        onCancel={() => {
          setDeleteConfirmVisible(false);
          setSelectedNovel(null);
        }}
      >
        <p>确定要删除小说 "{selectedNovel?.title}" 吗？此操作不可恢复。</p>
      </Modal>
    </>
  );
};

export default NovelsPage;