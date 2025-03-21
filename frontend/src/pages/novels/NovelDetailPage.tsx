import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import {
  Card,
  Row,
  Col,
  Tabs,
  Button,
  Space,
  Tag,
  Progress,
  List,
  Timeline,
  Empty,
  Statistic,
  Spin,
} from 'antd';
import {
  EditOutlined,
  HistoryOutlined,
  UserOutlined,
  RobotOutlined,
  FileTextOutlined,
  LineChartOutlined,
} from '@ant-design/icons';
import type { TabsProps } from 'antd';

import { useNovels } from '@/hooks/useNovels';
import { formatDateTime } from '@/utils/date';
import { ChapterList } from '@/components/novel/ChapterList';
import { CharacterList } from '@/components/novel/CharacterList';
import { ChapterEditor } from '@/components/novel/ChapterEditor';
import { NovelStats } from '@/components/novel/NovelStats';
import { GenerationHistory } from '@/components/novel/GenerationHistory';

const NovelDetailPage: React.FC = () => {
  const { novelId } = useParams<{ novelId: string }>();
  const [activeTabKey, setActiveTabKey] = useState('overview');
  const { novels, isLoading } = useNovels();

  const novel = novels?.find(n => n.id === Number(novelId));

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <Spin size="large" tip="加载中..." />
      </div>
    );
  }

  if (!novel) {
    return <Empty description="未找到小说" />;
  }

  const items: TabsProps['items'] = [
    {
      key: 'overview',
      label: '概览',
      children: (
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={16}>
            {/* 基本信息 */}
            <Card className="mb-4">
              <Row gutter={16}>
                <Col span={12}>
                  <Statistic
                    title="当前字数"
                    value={novel.current_word_count}
                    suffix="字"
                  />
                </Col>
                <Col span={12}>
                  <Statistic
                    title="总进度"
                    value={Math.round(
                      (novel.current_word_count / novel.target_word_count) * 100
                    )}
                    suffix="%"
                  />
                </Col>
              </Row>
              <Progress
                percent={Math.round(
                  (novel.current_word_count / novel.target_word_count) * 100
                )}
                status={novel.status === 'completed' ? 'success' : 'active'}
                className="mt-4"
              />
            </Card>

            {/* AI生成状态 */}
            <Card title="AI生成状态" className="mb-4">
              <Timeline>
                {novel.generation_history?.slice(-5).map((record, index) => (
                  <Timeline.Item key={index}>
                    <p className="font-medium">{record.action}</p>
                    <p className="text-sm text-gray-500">
                      {formatDateTime(record.created_at)}
                    </p>
                    {record.details && (
                      <p className="text-sm text-gray-600">{record.details}</p>
                    )}
                  </Timeline.Item>
                ))}
              </Timeline>
            </Card>

            {/* 最近章节 */}
            <Card title="最近章节">
              <List
                dataSource={novel.chapters?.slice(-5)}
                renderItem={chapter => (
                  <List.Item
                    actions={[
                      <Button
                        type="link"
                        onClick={() => setActiveTabKey('chapters')}
                      >
                        查看
                      </Button>,
                    ]}
                  >
                    <List.Item.Meta
                      title={chapter.title}
                      description={`${chapter.word_count}字 · ${formatDateTime(
                        chapter.updated_at
                      )}`}
                    />
                  </List.Item>
                )}
              />
            </Card>
          </Col>

          <Col xs={24} lg={8}>
            {/* 基本设置 */}
            <Card className="mb-4">
              <p>
                <strong>类型：</strong>
                <Tag>{novel.genre || '未分类'}</Tag>
              </p>
              <p>
                <strong>状态：</strong>
                <Tag color={novel.status === 'completed' ? 'success' : 'processing'}>
                  {novel.status}
                </Tag>
              </p>
              <p>
                <strong>创建时间：</strong>
                {formatDateTime(novel.created_at)}
              </p>
              <p>
                <strong>更新时间：</strong>
                {formatDateTime(novel.updated_at)}
              </p>
            </Card>

            {/* 统计信息 */}
            <Card title="统计信息">
              <NovelStats novel={novel} />
            </Card>
          </Col>
        </Row>
      ),
    },
    {
      key: 'chapters',
      label: '章节管理',
      children: <ChapterList novel={novel} />,
    },
    {
      key: 'characters',
      label: '人物管理',
      children: <CharacterList novel={novel} />,
    },
    {
      key: 'editor',
      label: '编辑器',
      children: <ChapterEditor novel={novel} />,
    },
    {
      key: 'history',
      label: '生成历史',
      children: <GenerationHistory novel={novel} />,
    },
  ];

  return (
    <Card
      title={novel.title}
      extra={
        <Space>
          <Button icon={<EditOutlined />}>编辑信息</Button>
          <Button type="primary" icon={<RobotOutlined />}>
            开始生成
          </Button>
        </Space>
      }
    >
      <Tabs
        activeKey={activeTabKey}
        items={items}
        onChange={key => setActiveTabKey(key)}
      />
    </Card>
  );
};

export default NovelDetailPage;