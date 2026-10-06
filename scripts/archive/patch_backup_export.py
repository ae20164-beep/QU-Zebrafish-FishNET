import re

backup_path = r'c:\Users\ae20164\OneDrive - Qatar University (1)\Zebrafish shared folder\FishNET Data\Labels\FishNET_Interactive_Dashboard_Standard_Backup.html'

with open(backup_path, 'r', encoding='utf-8') as f:
    c = f.read()

js_export = """
        function exportChartAsPNG(chartCanvasId, fileName) {
            const canvas = document.getElementById(chartCanvasId);
            if (!canvas) { alert('Canvas not found'); return; }
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = canvas.width;
            tempCanvas.height = canvas.height;
            const ctx = tempCanvas.getContext('2d');
            ctx.fillStyle = '#1e293b';
            ctx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
            ctx.drawImage(canvas, 0, 0);
            const link = document.createElement('a');
            link.download = (fileName || chartCanvasId) + '.png';
            link.href = tempCanvas.toDataURL('image/png', 1.0);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }

        function exportTableToCSV(tableId, fileName) {
            const table = document.getElementById(tableId) || document.querySelector('#' + tableId + ' table');
            if (!table) { alert('Table not found'); return; }
            let csv = [];
            const rows = table.querySelectorAll('tr');
            for (let i = 0; i < rows.length; i++) {
                let row = [], cols = rows[i].querySelectorAll('td, th');
                for (let j = 0; j < cols.length; j++) {
                    let text = cols[j].innerText.replace(/(\\r\\n|\\n|\\r)/gm, ' ').replace(/\\s+/g, ' ').trim();
                    text = text.replace(/"/g, '""');
                    row.push('"' + text + '"');
                }
                if (row.length > 0) csv.push(row.join(','));
            }
            const csvContent = 'data:text/csv;charset=utf-8,\\uFEFF' + encodeURIComponent(csv.join('\\n'));
            const link = document.createElement('a');
            link.setAttribute('href', csvContent);
            link.setAttribute('download', (fileName || 'table_export') + '.csv');
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
"""

if 'exportTableToCSV' not in c:
    c_new = c.replace('    </script>\n</body>', js_export + '\n    </script>\n</body>')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(c_new)
    print('Updated backup dashboard with export helpers.')
else:
    print('Export helpers already in backup dashboard.')
