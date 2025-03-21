import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Card,
  Form,
  Input,
  Select,
  InputNumber,
  Switch,
  Button,
  Space,
  Alert,
} from 'antd';
import { SaveOutlined, UndoOutlined } from '@ant-design/icons';

import { useMessage } from '@/hooks/useMessage';
import { useAgent } from '@/hooks/useAgent';
import type { AgentModelConfig, ModelProviderConfig } from '@/types';

const { Option } = Select;

const modelProviders = [
  { label: 'OpenAI', value: 'openai' },
  { label: 'Claude', value: 'claude' },
  { label: '本地模型', value: 'local' },
];

const AgentConfigPage: React.FC = () => {
  const { agentId } = useParams<{ agentId: string }>();
  const [form] = Form.useForm();
  const { showSuccess, showError } = useMessage();
  const { getAgentConfig, updateAgentConfig } = useAgent();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const config = await getAgentConfig(Number(agentId));
        form.setFieldsValue({
          ...config,
          ...config.provider_config,
          ...config.parameters,
          ...config.usage_limits,
        });
      } catch (error: any) {
        showError(error.message || '加载配置失败');
      }
    };

    fetchConfig();
  }, [agentId, form, getAgentConfig, showError]);

  const handleSubmit = async (values: any) => {
    try {
      setLoading(true);
      const config: AgentModelConfig = {
        agent_id: Number(agentId),
        provider_config: {
          provider: values.provider,
          model_name: values.model_name,
          api_key: values.api_key,
          organization_id: values.organization_id,
          base_url: values.base_url,
          extra_params: values.extra_params,
        },
        parameters: {
          temperature: values.temperature,
          max_tokens: values.max_tokens,
          top_p: values.top_p,
          frequency_penalty: values.frequency_penalty,
          presence_penalty: values.presence_penalty,
        },
        usage_limits: {
          max_requests_per_minute: values.max_requests_per_minute,
          max_tokens_per_request: values.max_tokens_per_request,
          max_daily_tokens: values.max_daily_tokens,
        },
        fallback_provider: values.fallback_provider,
      };

      await updateAgentConfig(Number(agentId), config);
      showSuccess('配置已更新');
    } catch (error: any) {
      showError(error.message || '更新配置失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card title="AI模型配置">
      <Alert
        message="配置说明"
        description="每个Agent可以配置不同的AI供应商和参数。请确保填写正确的API密钥和相关配置。"
        type="info"
        showIcon
        className="mb-6"
      />

      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          provider: 'openai',
          temperature: 0.7,
          max_tokens: 2048,
          top_p: 0.9,
          frequency_penalty: 0,
          presence_penalty: 0,
          max_requests_per_minute: 60,
          max_tokens_per_request: 4096,
          max_daily_tokens: 1000000,
        }}
      >
        <Card title="供应商配置" className="mb-6">
          <Form.Item
            name="provider"
            label="AI供应商"
            rules={[{ required: true }]}
          >
            <Select>
              {modelProviders.map((provider) => (
                <Option key={provider.value} value={provider.value}>
                  {provider.label}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="model_name"
            label="模型名称"
            rules={[{ required: true }]}
          >
            <Input placeholder="例如：gpt-4" />
          </Form.Item>

          <Form.Item
            name="api_key"
            label="API密钥"
            rules={[{ required: true }]}
          >
            <Input.Password placeholder="请输入API密钥" />
          </Form.Item>

          <Form.Item name="organization_id" label="组织ID">
            <Input placeholder="可选" />
          </Form.Item>

          <Form.Item name="base_url" label="API基础URL">
            <Input placeholder="可选，用于自定义API端点" />
          </Form.Item>
        </Card>

        <Card title="模型参数" className="mb-6">
          <Form.Item
            name="temperature"
            label="温度系数"
            rules={[{ required: true }]}
          >
            <InputNumber
              min={0}
              max={2}
              step={0.1}
              style={{ width: '100%' }}
            />
          </Form.Item>

          <Form.Item
            name="max_tokens"
            label="最大Token数"
            rules={[{ required: true }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="top_p" label="Top P" rules={[{ required: true }]}>
            <InputNumber
              min={0}
              max={1}
              step={0.1}
              style={{ width: '100%' }}
            />
          </Form.Item>

          <Form.Item
            name="frequency_penalty"
            label="频率惩罚"
            rules={[{ required: true }]}
          >
            <InputNumber
              min={-2}
              max={2}
              step={0.1}
              style={{ width: '100%' }}
            />
          </Form.Item>

          <Form.Item
            name="presence_penalty"
            label="存在惩罚"
            rules={[{ required: true }]}
          >
            <InputNumber
              min={-2}
              max={2}
              step={0.1}
              style={{ width: '100%' }}
            />
          </Form.Item>
        </Card>

        <Card title="使用限制" className="mb-6">
          <Form.Item
            name="max_requests_per_minute"
            label="每分钟最大请求数"
            rules={[{ required: true }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="max_tokens_per_request"
            label="单次请求最大Token数"
            rules={[{ required: true }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item
            name="max_daily_tokens"
            label="每日最大Token数"
            rules={[{ required: true }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
        </Card>

        <Form.Item name="fallback_provider" label="备用供应商">
          <Select allowClear>
            {modelProviders.map((provider) => (
              <Option key={provider.value} value={provider.value}>
                {provider.label}
              </Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item>
          <Space>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              htmlType="submit"
              loading={loading}
            >
              保存配置
            </Button>
            <Button icon={<UndoOutlined />} onClick={() => form.resetFields()}>
              重置表单
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default AgentConfigPage;