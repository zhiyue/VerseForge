import React, { useEffect } from 'react';
import { Card, Row, Col, Statistic, Progress, List, Tag, Timeline } from 'antd';
import {
  BookOutlined,
  RobotOutlined,
  LineChartOutlined,
  ClockCircleOutlined,
} from '@ant-design/icons';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

import { useNovels } from '@/hooks/useNovels';
import { useAgent } from '@/hooks/useAgent';
import { formatDateTime } from '@/utils/date';

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const DashboardPage: React.FC = () => {
  const { novels, isLoading: novelsLoading } = useNovels();
  const { agents, isLoading: agentsLoading } = useAgent();

  // 统计数据
  const totalNovels = novels?.length || 0;
  const completedNovels = novels?.filter(n => n.status === 'completed').length || 0;
  const activeAgents = agents?.filter(a => a.status === 'working').length || 0;
  const totalWords = novels?.reduce((acc, n) => acc + n.current_word_count, 0) || 0;

  // 每日写作数据
  const writingData = {
    labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    datasets: [
      {
        label: '写作字数',
        data: [3000, 5000, 4000, 6000, 5500, 4800, 7000],
        fill: false,
        borderColor: '#1677ff',
        tension: 0.1,
      },
    ],
  };

  // 最近任务
  const recentTasks = [
    {
      id: 1,
      title: '生成章节大纲',
      status: 'success',
      time: '10分钟前',
    },
    {
      id: 2,
      title: '人物对话优化',
      status: 'processing',
      time: '30分钟前',
    },
    {
      id: 3,
      title: '情节连贯性检查',
      status: 'error',
      time: '1小时前',
    },
  ];

  return (
    <div className="dashboard">
      {/* 统计卡片 */}
      <Row gutter={[16, 16]} className="mb-6">
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总作品数"
              value={totalNovels}
              prefix={<BookOutlined />}
              loading={novelsLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="活跃智能体"
              value={activeAgents}
              prefix={<RobotOutlined />}
              loading={agentsLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="完成作品"
              value={completedNovels}
              prefix={<LineChartOutlined />}
              loading={novelsLoading}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总字数"
              value={totalWords}
              prefix={<ClockCircleOutlined />}
              loading={novelsLoading}
            />
          </Card>
        </Col>
      </Row>

      {/* 图表和列表 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={16}>
          <Card title="写作进度" className="mb-6">
            <Line data={writingData} />
          </Card>
          <Card title="最近作品">
            <List
              dataSource={novels?.slice(0, 5)}
              loading={novelsLoading}
              renderItem={novel => (
                <List.Item
                  actions={[
                    <Tag color={novel.status === 'completed' ? 'success' : 'processing'}>
                      {novel.status}
                    </Tag>,
                  ]}
                >
                  <List.Item.Meta
                    title={novel.title}
                    description={`${novel.current_word_count}字 / ${novel.target_word_count}字`}
                  />
                  <Progress
                    percent={Math.round(
                      (novel.current_word_count / novel.target_word_count) * 100
                    )}
                    size="small"
                    status={novel.status === 'completed' ? 'success' : 'active'}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card title="AI助手状态" className="mb-6">
            <List
              dataSource={agents?.slice(0, 5)}
              loading={agentsLoading}
              renderItem={agent => (
                <List.Item>
                  <List.Item.Meta
                    title={agent.name}
                    description={
                      <Tag color={agent.status === 'working' ? 'processing' : 'default'}>
                        {agent.status}
                      </Tag>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
          <Card title="最近任务">
            <Timeline>
              {recentTasks.map(task => (
                <Timeline.Item key={task.id} color={task.status}>
                  <div className="font-medium">{task.title}</div>
                  <div className="text-sm text-gray-500">{task.time}</div>
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;