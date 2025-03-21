import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  Table,
  Button,
  Space,
  Tag,
  Modal,
  Tooltip,
  Badge,
  Statistic,
} from 'antd';
import {
  PlusOutlined,
  SettingOutlined,
  ReloadOutlined,
  DeleteOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

import { useAgent } from '@/hooks/useAgent';
import type { Agent } from '@/types';
import { formatDateTime } from '@/utils/date';

const AgentsPage: React.FC = () => {
  const navigate = useNavigate();
  const { agents, isLoading, deleteAgent, resetAgent } = useAgent();
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'idle':
        return 'success';
      case 'working':
        return 'processing';
      case 'error':
        return 'error';
      case 'paused':
        return 'warning';
      default:
        return 'default';
    }
  };

  const columns: ColumnsType<Agent> = [
    {
      title: '名称',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          <Badge status={getStatusColor(record.status) as any} />
          {text}
        </Space>
      ),
    },
    {
      title: '类型',
      dataIndex: 'agent_type',
      key: 'agent_type',
      render: (text) => <Tag>{text}</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={getStatusColor(status)}>{status.toUpperCase()}</Tag>
      ),
    },
    {
      title: '性能统计',
      key: 'stats',
      render: (_, record) => (
        <Space>
          <Statistic
            title="成功率"
            value={record.stats?.success_rate ?? 0}
            suffix="%"
            precision={2}
            valueStyle={{ fontSize: '14px' }}
          />
          <Statistic
            title="平均响应时间"
            value={record.stats?.avg_response_time ?? 0}
            suffix="ms"
            precision={0}
            valueStyle={{ fontSize: '14px' }}
          />
        </Space>
      ),
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
          <Tooltip title="配置">
            <Button
              type="text"
              icon={<SettingOutlined />}
              onClick={() => navigate(`/agents/${record.id}/config`)}
            />
          </Tooltip>
          <Tooltip title="重置">
            <Button
              type="text"
              icon={<ReloadOutlined />}
              onClick={() => handleReset(record)}
            />
          </Tooltip>
          <Tooltip title="删除">
            <Button
              type="text"
              danger
              icon={<DeleteOutlined />}
              onClick={() => setSelectedAgent(record)}
            />
          </Tooltip>
        </Space>
      ),
    },
  ];

  const handleDelete = async () => {
    if (selectedAgent) {
      await deleteAgent(selectedAgent.id);
      setSelectedAgent(null);
    }
  };

  const handleReset = async (agent: Agent) => {
    await resetAgent(agent.id);
  };

  return (
    <>
      <Card
        title="AI智能体管理"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate('/agents/create')}
          >
            创建智能体
          </Button>
        }
      >
        <Table
          columns={columns}
          dataSource={agents}
          loading={isLoading}
          rowKey="id"
          pagination={{
            showQuickJumper: true,
            showSizeChanger: true,
            showTotal: (total) => `共 ${total} 条`,
          }}
        />
      </Card>

      <Modal
        title="确认删除"
        open={!!selectedAgent}
        onOk={handleDelete}
        onCancel={() => setSelectedAgent(null)}
        okText="确认"
        cancelText="取消"
      >
        <p>
          确定要删除智能体 "{selectedAgent?.name}" 吗？此操作不可恢复。
        </p>
      </Modal>
    </>
  );
};

export default AgentsPage;