import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

/**
 * 导出检测记录为Excel
 */
export function exportDetectionRecords(records, filename = '检测记录') {
  const data = records.map(record => ({
    '记录ID': record.id,
    '源类型': getSourceTypeName(record.sourceType),
    '检测时间': record.createdAt,
    '是否异常': record.hasAbnormal ? '是' : '否',
    '行为类型': getBehaviorTypeName(record.behaviorType),
    '置信度': record.confidence ? `${(record.confidence * 100).toFixed(1)}%` : '-',
    '状态': getStatusName(record.status)
  }))
  
  exportToExcel(data, filename)
}

/**
 * 导出告警记录为Excel
 */
export function exportAlerts(alerts, filename = '告警记录') {
  const data = alerts.map(alert => ({
    '告警ID': alert.id,
    '告警类型': alert.alertType,
    '告警级别': alert.alertLevel,
    '置信度': `${(alert.confidence * 100).toFixed(1)}%`,
    '描述': alert.description,
    '是否已读': alert.isRead ? '是' : '否',
    '是否已处理': alert.isHandled ? '是' : '否',
    '处理人': alert.handledBy || '-',
    '处理时间': alert.handledAt || '-',
    '告警时间': alert.createdAt
  }))
  
  exportToExcel(data, filename)
}

/**
 * 导出统计报表为Excel
 */
export function exportStatistics(statistics, filename = '统计报表') {
  // 创建工作簿
  const wb = XLSX.utils.book_new()
  
  // 概览数据
  const overviewData = [
    ['统计项', '数值'],
    ['检测总次数', statistics.total_records || 0],
    ['异常检测次数', statistics.abnormal_records || 0],
    ['正常检测次数', statistics.normal_records || 0]
  ]
  const overviewSheet = XLSX.utils.aoa_to_sheet(overviewData)
  XLSX.utils.book_append_sheet(wb, overviewSheet, '概览')
  
  // 行为类型统计
  if (statistics.behavior_type_stats) {
    const behaviorData = [
      ['行为类型', '次数'],
      ['跌倒', statistics.behavior_type_stats.FALL || 0],
      ['打架', statistics.behavior_type_stats.FIGHT || 0],
      ['异常姿态', statistics.behavior_type_stats.ABNORMAL_POSE || 0]
    ]
    const behaviorSheet = XLSX.utils.aoa_to_sheet(behaviorData)
    XLSX.utils.book_append_sheet(wb, behaviorSheet, '行为类型统计')
  }
  
  // 7天趋势
  if (statistics.trend_7_days) {
    const trendData = [
      ['日期', '检测次数', '异常次数', '正常次数']
    ]
    statistics.trend_7_days.forEach(item => {
      trendData.push([
        item.date,
        item.total_count,
        item.abnormal_count,
        item.normal_count
      ])
    })
    const trendSheet = XLSX.utils.aoa_to_sheet(trendData)
    XLSX.utils.book_append_sheet(wb, trendSheet, '7天趋势')
  }
  
  // 导出
  XLSX.writeFile(wb, `${filename}_${getTimestamp()}.xlsx`)
}

/**
 * 通用Excel导出函数
 */
function exportToExcel(data, filename) {
  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Sheet1')
  XLSX.writeFile(wb, `${filename}_${getTimestamp()}.xlsx`)
}

/**
 * 导出为CSV
 */
export function exportToCSV(data, filename) {
  const ws = XLSX.utils.json_to_sheet(data)
  const csv = XLSX.utils.sheet_to_csv(ws)
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' })
  saveAs(blob, `${filename}_${getTimestamp()}.csv`)
}

/**
 * 导出为JSON
 */
export function exportToJSON(data, filename) {
  const json = JSON.stringify(data, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  saveAs(blob, `${filename}_${getTimestamp()}.json`)
}

/**
 * 打印表格数据
 */
export function printTable(title, columns, data) {
  const printWindow = window.open('', '_blank')
  
  let tableHtml = `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>${title}</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          padding: 20px;
        }
        h1 {
          text-align: center;
          color: #333;
          margin-bottom: 20px;
        }
        table {
          width: 100%;
          border-collapse: collapse;
          margin-top: 20px;
        }
        th, td {
          border: 1px solid #ddd;
          padding: 12px;
          text-align: left;
        }
        th {
          background-color: #409eff;
          color: white;
          font-weight: bold;
        }
        tr:nth-child(even) {
          background-color: #f9f9f9;
        }
        tr:hover {
          background-color: #f5f5f5;
        }
        .print-footer {
          margin-top: 30px;
          text-align: center;
          color: #666;
          font-size: 12px;
        }
        @media print {
          body {
            padding: 10px;
          }
          .no-print {
            display: none;
          }
        }
      </style>
    </head>
    <body>
      <h1>${title}</h1>
      <table>
        <thead>
          <tr>
  `
  
  columns.forEach(col => {
    tableHtml += `<th>${col.label}</th>`
  })
  
  tableHtml += `
          </tr>
        </thead>
        <tbody>
  `
  
  data.forEach(row => {
    tableHtml += '<tr>'
    columns.forEach(col => {
      let value = row[col.prop]
      if (col.formatter) {
        value = col.formatter(row)
      }
      tableHtml += `<td>${value || '-'}</td>`
    })
    tableHtml += '</tr>'
  })
  
  tableHtml += `
        </tbody>
      </table>
      <div class="print-footer">
        打印时间：${new Date().toLocaleString('zh-CN')}
      </div>
      <div class="no-print" style="text-align: center; margin-top: 20px;">
        <button onclick="window.print()" style="padding: 10px 30px; font-size: 16px; cursor: pointer;">打印</button>
        <button onclick="window.close()" style="padding: 10px 30px; font-size: 16px; cursor: pointer; margin-left: 10px;">关闭</button>
      </div>
    </body>
    </html>
  `
  
  printWindow.document.write(tableHtml)
  printWindow.document.close()
}

// 辅助函数
function getTimestamp() {
  const now = new Date()
  return `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}_${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}`
}

function getSourceTypeName(type) {
  const map = {
    'IMAGE': '图片',
    'VIDEO': '视频',
    'CAMERA': '摄像头',
    'RTSP': 'RTSP流'
  }
  return map[type] || type
}

function getBehaviorTypeName(type) {
  const map = {
    'FALL': '跌倒',
    'FIGHT': '打架',
    'ABNORMAL_POSE': '异常姿态'
  }
  return map[type] || '-'
}

function getStatusName(status) {
  const map = {
    'PROCESSING': '处理中',
    'COMPLETED': '已完成',
    'FAILED': '失败'
  }
  return map[status] || status
}

