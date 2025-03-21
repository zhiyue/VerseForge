import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/apiClient';
import type { Novel } from '@/types';
import { useMessage } from './useMessage';

export interface NovelCreateData {
  title: string;
  description?: string;
  genre?: string;
  target_word_count: number;
}

export interface NovelUpdateData {
  title?: string;
  description?: string;
  genre?: string;
  target_word_count?: number;
  status?: string;
}

export interface NovelFilters {
  status?: string;
  genre?: string;
  search?: string;
}

export const useNovels = (filters?: NovelFilters) => {
  const queryClient = useQueryClient();
  const { showSuccess, showError } = useMessage();

  // 获取小说列表
  const {
    data: novels,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['novels', filters],
    queryFn: () =>
      api.get<Novel[]>('/novels', {
        params: filters,
      }),
  });

  // 创建小说
  const createNovelMutation = useMutation({
    mutationFn: (data: NovelCreateData) => api.post<Novel>('/novels', data),
    onSuccess: () => {
      showSuccess('小说创建成功');
      queryClient.invalidateQueries(['novels']);
    },
    onError: (error: any) => {
      showError(error.message || '小说创建失败');
    },
  });

  // 更新小说
  const updateNovelMutation = useMutation({
    mutationFn: ({ id, data }: { id: number; data: NovelUpdateData }) =>
      api.put<Novel>(`/novels/${id}`, data),
    onSuccess: () => {
      showSuccess('小说更新成功');
      queryClient.invalidateQueries(['novels']);
    },
    onError: (error: any) => {
      showError(error.message || '小说更新失败');
    },
  });

  // 删除小说
  const deleteNovelMutation = useMutation({
    mutationFn: (id: number) => api.delete<void>(`/novels/${id}`),
    onSuccess: () => {
      showSuccess('小说删除成功');
      queryClient.invalidateQueries(['novels']);
    },
    onError: (error: any) => {
      showError(error.message || '小说删除失败');
    },
  });

  // 开始生成小说
  const startGenerationMutation = useMutation({
    mutationFn: (id: number) => api.post<void>(`/novels/${id}/generate`),
    onSuccess: () => {
      showSuccess('开始生成小说');
      queryClient.invalidateQueries(['novels']);
    },
    onError: (error: any) => {
      showError(error.message || '启动生成失败');
    },
  });

  // 暂停生成小说
  const pauseGenerationMutation = useMutation({
    mutationFn: (id: number) => api.post<void>(`/novels/${id}/pause`),
    onSuccess: () => {
      showSuccess('已暂停生成');
      queryClient.invalidateQueries(['novels']);
    },
    onError: (error: any) => {
      showError(error.message || '暂停失败');
    },
  });

  return {
    novels,
    isLoading,
    error,
    createNovel: (data: NovelCreateData) => createNovelMutation.mutateAsync(data),
    updateNovel: (id: number, data: NovelUpdateData) =>
      updateNovelMutation.mutateAsync({ id, data }),
    deleteNovel: (id: number) => deleteNovelMutation.mutateAsync(id),
    startGeneration: (id: number) => startGenerationMutation.mutateAsync(id),
    pauseGeneration: (id: number) => pauseGenerationMutation.mutateAsync(id),
  };
};