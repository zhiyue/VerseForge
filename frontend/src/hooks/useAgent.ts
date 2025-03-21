import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/apiClient';
import type { Agent, AgentModelConfig } from '@/types';
import { useMessage } from './useMessage';

export const useAgent = () => {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useMessage();

  // 获取Agent列表
  const { data: agents, isLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: () => api.get<Agent[]>('/agents'),
  });

  // 获取Agent配置
  const getAgentConfig = async (agentId: number) => {
    return api.get<AgentModelConfig>(`/agents/${agentId}/config`);
  };

  // 更新Agent配置
  const updateConfigMutation = useMutation({
    mutationFn: (params: { agentId: number; config: AgentModelConfig }) =>
      api.put(`/agents/${params.agentId}/config`, params.config),
    onSuccess: () => {
      showSuccess('配置更新成功');
      queryClient.invalidateQueries(['agents']);
    },
    onError: (error: any) => {
      showError(error.message || '配置更新失败');
    },
  });

  // 重置Agent
  const resetAgentMutation = useMutation({
    mutationFn: (agentId: number) => api.post(`/agents/${agentId}/reset`),
    onSuccess: () => {
      showSuccess('Agent已重置');
      queryClient.invalidateQueries(['agents']);
    },
    onError: (error: any) => {
      showError(error.message || 'Agent重置失败');
    },
  });

  // 创建Agent
  const createAgentMutation = useMutation({
    mutationFn: (data: Partial<Agent>) => api.post('/agents', data),
    onSuccess: () => {
      showSuccess('Agent创建成功');
      queryClient.invalidateQueries(['agents']);
    },
    onError: (error: any) => {
      showError(error.message || 'Agent创建失败');
    },
  });

  // 更新Agent
  const updateAgentMutation = useMutation({
    mutationFn: (params: { agentId: number; data: Partial<Agent> }) =>
      api.put(`/agents/${params.agentId}`, params.data),
    onSuccess: () => {
      showSuccess('Agent更新成功');
      queryClient.invalidateQueries(['agents']);
    },
    onError: (error: any) => {
      showError(error.message || 'Agent更新失败');
    },
  });

  // 删除Agent
  const deleteAgentMutation = useMutation({
    mutationFn: (agentId: number) => api.delete(`/agents/${agentId}`),
    onSuccess: () => {
      showSuccess('Agent删除成功');
      queryClient.invalidateQueries(['agents']);
    },
    onError: (error: any) => {
      showError(error.message || 'Agent删除失败');
    },
  });

  return {
    agents,
    isLoading,
    getAgentConfig,
    updateAgentConfig: (agentId: number, config: AgentModelConfig) =>
      updateConfigMutation.mutateAsync({ agentId, config }),
    resetAgent: (agentId: number) => resetAgentMutation.mutateAsync(agentId),
    createAgent: (data: Partial<Agent>) => createAgentMutation.mutateAsync(data),
    updateAgent: (agentId: number, data: Partial<Agent>) =>
      updateAgentMutation.mutateAsync({ agentId, data }),
    deleteAgent: (agentId: number) => deleteAgentMutation.mutateAsync(agentId),
  };
};