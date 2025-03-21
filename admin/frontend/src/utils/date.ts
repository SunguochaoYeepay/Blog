export function formatDate(dateStr: string | null): string {
  if (!dateStr) return '从未登录';
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000));
    if (hours < 1) {
      const minutes = Math.floor(diff / (60 * 1000));
      return `${minutes} 分钟前`;
    }
    return `${hours} 小时前`;
  }
  
  return date.toLocaleString();
} 