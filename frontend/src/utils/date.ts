import dayjs from 'dayjs';
import 'dayjs/locale/zh-cn';
import relativeTime from 'dayjs/plugin/relativeTime';
import calendar from 'dayjs/plugin/calendar';
import updateLocale from 'dayjs/plugin/updateLocale';

// 配置dayjs
dayjs.locale('zh-cn');
dayjs.extend(relativeTime);
dayjs.extend(calendar);
dayjs.extend(updateLocale);

// 更新中文语言配置
dayjs.updateLocale('zh-cn', {
  calendar: {
    lastDay: '[昨天] HH:mm',
    sameDay: '[今天] HH:mm',
    nextDay: '[明天] HH:mm',
    lastWeek: '[上]dddd HH:mm',
    nextWeek: '[下]dddd HH:mm',
    sameElse: 'YYYY-MM-DD HH:mm',
  },
});

/**
 * 格式化日期时间
 * @param date - 日期时间字符串或Date对象
 * @param format - 格式化模式（可选）
 */
export const formatDateTime = (
  date: string | Date | null | undefined,
  format = 'YYYY-MM-DD HH:mm:ss'
): string => {
  if (!date) return '-';
  return dayjs(date).format(format);
};

/**
 * 格式化日期
 * @param date - 日期字符串或Date对象
 * @param format - 格式化模式（可选）
 */
export const formatDate = (
  date: string | Date | null | undefined,
  format = 'YYYY-MM-DD'
): string => {
  if (!date) return '-';
  return dayjs(date).format(format);
};

/**
 * 获取相对时间
 * @param date - 日期时间字符串或Date对象
 */
export const getRelativeTime = (date: string | Date | null | undefined): string => {
  if (!date) return '-';
  return dayjs(date).fromNow();
};

/**
 * 获取日历时间
 * @param date - 日期时间字符串或Date对象
 */
export const getCalendarTime = (date: string | Date | null | undefined): string => {
  if (!date) return '-';
  return dayjs(date).calendar();
};

/**
 * 检查日期是否有效
 * @param date - 日期时间字符串或Date对象
 */
export const isValidDate = (date: string | Date | null | undefined): boolean => {
  if (!date) return false;
  return dayjs(date).isValid();
};

/**
 * 获取两个日期之间的天数
 * @param start - 开始日期
 * @param end - 结束日期
 */
export const getDaysBetween = (
  start: string | Date,
  end: string | Date
): number => {
  return dayjs(end).diff(dayjs(start), 'day');
};

/**
 * 将时间戳转换为日期时间字符串
 * @param timestamp - 时间戳（毫秒）
 * @param format - 格式化模式（可选）
 */
export const timestampToDateTime = (
  timestamp: number,
  format = 'YYYY-MM-DD HH:mm:ss'
): string => {
  return dayjs(timestamp).format(format);
};