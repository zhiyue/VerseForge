# VerseForge 前端

基于React + TypeScript + Ant Design开发的网文创作平台前端。

## 技术栈

- React 18
- TypeScript 5
- Ant Design 5
- TailwindCSS
- React Query
- Redux Toolkit
- Vite 5

## 目录结构

```bash
src/
├── assets/         # 静态资源
├── components/     # 公共组件
├── hooks/          # 自定义Hooks
├── pages/          # 页面组件
├── services/       # API服务
├── store/          # 状态管理
├── styles/         # 样式文件
├── types/          # 类型定义
├── utils/          # 工具函数
├── App.tsx         # 根组件
└── main.tsx        # 入口文件
```

## 开发环境要求

- Node.js 18+
- yarn 1.22+

## 安装依赖

```bash
yarn install
```

## 开发

```bash
# 启动开发服务器
yarn dev

# 类型检查
yarn type-check

# 代码格式化
yarn format

# 代码检查
yarn lint
```

## 构建

```bash
# 构建生产版本
yarn build

# 预览生产构建
yarn preview
```

## 特性

- 📦 基于Vite的现代构建系统
- 🎨 集成TailwindCSS和Ant Design的UI系统
- 🔄 React Query数据管理
- 🌐 多环境配置
- 📱 响应式设计
- 🔒 类型安全
- 🚀 自动优化和代码分割

## 代码规范

- 使用TypeScript编写所有代码
- 遵循ESLint和Prettier配置
- 使用函数组件和Hooks
- 按功能模块组织代码
- 编写单元测试

## 模块说明

### 组件结构

- `components/layout`: 布局组件
- `components/auth`: 认证相关组件
- `components/common`: 通用组件
- `components/form`: 表单组件

### 状态管理

- React Query用于服务器状态
- Redux Toolkit用于客户端状态
- Context API用于主题等全局配置

### API集成

- Axios实例配置
- 请求/响应拦截器
- 错误处理
- 自动刷新Token

### 路由管理

- 基于React Router 6
- 路由权限控制
- 路由懒加载

### UI/UX

- 响应式设计
- 深色模式支持
- 动画效果
- 加载状态处理

### 性能优化

- 代码分割
- 资源预加载
- 图片懒加载
- 虚拟滚动

### 安全

- XSS防护
- CSRF防护
- 敏感信息加密
- 输入验证

## 环境变量

在 `.env` 文件中配置：

```bash
VITE_API_URL=         # API基础URL
VITE_APP_ENV=         # 环境标识
VITE_ENABLE_MOCK=     # 是否启用Mock
VITE_ENABLE_LOGGER=   # 是否启用日志
```

## 部署

1. 构建项目
```bash
yarn build
```

2. 将 `dist` 目录下的文件部署到服务器

3. 配置nginx：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8000/;
    }
}
```

## 测试

```bash
# 运行单元测试
yarn test

# 生成测试覆盖率报告
yarn test:coverage
```

## TODO

- [ ] 添加E2E测试
- [ ] 优化首屏加载
- [ ] 实现PWA
- [ ] 添加错误边界
- [ ] 国际化支持