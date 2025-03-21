import { message } from 'antd';
import { useCallback } from 'react';

export interface MessageHook {
  showSuccess: (content: string) => void;
  showError: (content: string) => void;
  showWarning: (content: string) => void;
  showInfo: (content: string) => void;
  messageApi: React.ReactElement;
}

export const useMessage = (): MessageHook => {
  const [messageApi, contextHolder] = message.useMessage();

  const showSuccess = useCallback(
    (content: string) => {
      messageApi.success(content);
    },
    [messageApi]
  );

  const showError = useCallback(
    (content: string) => {
      messageApi.error(content);
    },
    [messageApi]
  );

  const showWarning = useCallback(
    (content: string) => {
      messageApi.warning(content);
    },
    [messageApi]
  );

  const showInfo = useCallback(
    (content: string) => {
      messageApi.info(content);
    },
    [messageApi]
  );

  return {
    showSuccess,
    showError,
    showWarning,
    showInfo,
    messageApi: contextHolder
  };
};