import { AxiosRequestConfig, AxiosResponse } from 'axios';

// 通用类型
export interface ApiPaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// 用户相关类型
export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

// 小说相关类型
export interface Novel {
  id: number;
  title: string;
  description: string;
  genre: string;
  target_word_count: number;
  current_word_count: number;
  status: string;
  creator_id: number;
  created_at: string;
  updated_at: string;
}

export interface Chapter {
  id: number;
  novel_id: number;
  chapter_number: number;
  title: string;
  content: string;
  word_count: number;
  status: string;
  created_at: string;
  updated_at: string;
}

// Agent相关类型
export interface Agent {
  id: number;
  name: string;
  agent_type: string;
  status: string;
  parameters: Record<string, any>;
  stats: Record<string, any>;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface AgentTask {
  id: number;
  agent_id: number;
  novel_id: number;
  task_type: string;
  task_data: Record<string, any>;
  priority: number;
  status: string;
  result?: Record<string, any>;
  error_message?: string;
  created_at: string;
  updated_at: string;
}

// 模型配置相关类型
export interface ModelProviderConfig {
  provider: string;
  model_name: string;
  api_key: string;
  organization_id?: string;
  base_url?: string;
  extra_params?: Record<string, any>;
}

export interface AgentModelConfig {
  agent_id: number;
  provider_config: ModelProviderConfig;
  parameters: {
    temperature: number;
    max_tokens: number;
    top_p: number;
    frequency_penalty: number;
    presence_penalty: number;
  };
  usage_limits: {
    max_requests_per_minute: number;
    max_tokens_per_request: number;
    max_daily_tokens: number;
  };
  fallback_provider?: string;
}

// API请求响应类型
export interface ApiRequestConfig extends AxiosRequestConfig {
  skipErrorHandler?: boolean;
}

export interface ApiError {
  code: string;
  message: string;
  details?: any;
}

export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  code?: string;
}

// 组件Props类型
export interface TableProps {
  loading?: boolean;
  data: any[];
  columns: any[];
  pagination?: {
    current: number;
    pageSize: number;
    total: number;
  };
  onChange?: (pagination: any, filters: any, sorter: any) => void;
}

export interface FormProps {
  initialValues?: Record<string, any>;
  onSubmit: (values: any) => void;
  onCancel?: () => void;
  loading?: boolean;
}

export interface ModalProps {
  visible: boolean;
  title: string;
  onOk: () => void;
  onCancel: () => void;
  loading?: boolean;
  width?: number | string;
}