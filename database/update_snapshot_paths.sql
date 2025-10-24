-- 更新告警快照路径
-- 将完整URL转换为相对路径

-- 更新 snapshot_path，移除 http://localhost:5000/ 前缀
UPDATE alerts 
SET snapshot_path = REPLACE(snapshot_path, 'http://localhost:5000/', '')
WHERE snapshot_path LIKE 'http://localhost:5000/%';

-- 验证更新结果
SELECT 
    id, 
    alert_type, 
    snapshot_path,
    created_at
FROM alerts 
WHERE snapshot_path IS NOT NULL
ORDER BY created_at DESC
LIMIT 10;

