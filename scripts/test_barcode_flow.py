import asyncio
import json
import subprocess
import time
import urllib.request
import websockets
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

async def main():
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    labels_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    index_file = os.path.join(labels_dir, "index.html")
    file_url = "file:///" + index_file.replace("\\", "/")

    print(f"Launching Chrome with: {file_url}")
    proc = subprocess.Popen([
        chrome_path,
        "--headless=new",
        "--remote-debugging-port=9229",
        "--disable-gpu",
        "--no-sandbox",
        "--allow-file-access-from-files",
        file_url
    ])
    await asyncio.sleep(3)

    try:
        with urllib.request.urlopen("http://127.0.0.1:9229/json") as resp:
            targets = json.loads(resp.read().decode())
        
        page_target = next(t for t in targets if "index.html" in t.get("url", ""))
        ws_url = page_target["webSocketDebuggerUrl"]
        
        async with websockets.connect(ws_url) as ws:
            await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
            
            # Step 1: Check initial page state and elements
            test_js_1 = """({
                tanksLoaded: Object.keys(currentTanks).length,
                hasFab: !!document.getElementById('fabScanTank'),
                hasScannerModal: !!document.getElementById('modalBarcodeScanner'),
                hasScannerReader: !!document.getElementById('barcodeScannerReader'),
                kpiSubtext: document.getElementById('kpiTankStatusSub')?.innerText
            })"""
            
            await ws.send(json.dumps({
                "id": 2,
                "method": "Runtime.evaluate",
                "params": {"expression": test_js_1, "returnByValue": True}
            }))

            start = time.time()
            res1 = None
            while time.time() - start < 5:
                msg = json.loads(await ws.recv())
                if msg.get("id") == 2:
                    res1 = msg["result"]["result"]["value"]
                    break
            print("TEST 1 (Elements & Init):", res1)

            # Step 2: Test Barcode Normalizer logic in browser runtime
            test_js_2 = """({
                t0056: normalizeScannedBarcode('T0056'),
                num56: normalizeScannedBarcode('56'),
                t56: normalizeScannedBarcode('t56'),
                tank185: normalizeScannedBarcode('Tank: 185'),
                url135: normalizeScannedBarcode('https://qu.edu.qa/?tank=T0135'),
                t0011: normalizeScannedBarcode('T11')
            })"""

            await ws.send(json.dumps({
                "id": 3,
                "method": "Runtime.evaluate",
                "params": {"expression": test_js_2, "returnByValue": True}
            }))

            start = time.time()
            res2 = None
            while time.time() - start < 5:
                msg = json.loads(await ws.recv())
                if msg.get("id") == 3:
                    res2 = msg["result"]["result"]["value"]
                    break
            print("TEST 2 (Barcode Normalizer):", res2)

            # Step 3: Test Opening Scanner and Submitting Manual/Simulated Barcode Scan
            test_js_3 = """(() => {
                openBarcodeScanner();
                const modalVisible = document.getElementById('modalBarcodeScanner').style.display === 'flex';
                
                // Simulate scan success for T0056
                onBarcodeScanSuccess('T0056');
                
                const scannerClosed = document.getElementById('modalBarcodeScanner').style.display === 'none';
                const editModalOpen = document.getElementById('modalEditRow').style.display === 'flex';
                const editTankIdVal = document.getElementById('editTankId').value;
                const modalTitle = document.getElementById('editModalTitle').innerText;

                return {
                    modalOpened: modalVisible,
                    scannerClosedAfterScan: scannerClosed,
                    editModalOpen: editModalOpen,
                    editTankId: editTankIdVal,
                    modalTitle: modalTitle
                };
            })()"""

            await ws.send(json.dumps({
                "id": 4,
                "method": "Runtime.evaluate",
                "params": {"expression": test_js_3, "returnByValue": True}
            }))

            start = time.time()
            res3 = None
            while time.time() - start < 5:
                msg = json.loads(await ws.recv())
                if msg.get("id") == 4:
                    res3 = msg["result"]["result"]["value"]
                    break
            print("TEST 3 (Scanner Flow & Modal Open):", res3)

            # Step 4: Test Saving Edit and verifying cascading updates across Tabs & KPIs
            test_js_4 = """(() => {
                // Mock alert to prevent blocking modal
                window.alert = function(m) { console.log('Mock alert:', m); };

                // Get baseline active count
                const baseActive = Object.values(currentTanks).filter(t => t.status === 'Active').length;

                // Edit T0056: switch to Active with 8 females and 6 males
                document.getElementById('editTankStatus').value = 'Active';
                document.getElementById('editTankFemale').value = '8';
                document.getElementById('editTankMale').value = '6';
                document.getElementById('editTankNotes').value = 'Tested via Mobile Barcode Scanner';
                saveTankEdit();

                const afterActive = Object.values(currentTanks).filter(t => t.status === 'Active').length;
                const kpiAfter = document.getElementById('kpiTankStatusSub').innerText;
                const t0056Obj = currentTanks['T0056'];
                const storedOverrides = JSON.parse(localStorage.getItem('fishnet_user_tank_overrides') || '{}');

                // Now switch T0056 back to Euthanized
                openEditTankModal('T0056');
                document.getElementById('editTankStatus').value = 'Euthanized';
                document.getElementById('editTankFemale').value = '0';
                document.getElementById('editTankMale').value = '0';
                saveTankEdit();

                const finalActive = Object.values(currentTanks).filter(t => t.status === 'Active').length;
                const kpiFinal = document.getElementById('kpiTankStatusSub').innerText;

                return {
                    baseActive: baseActive,
                    afterActive: afterActive,
                    kpiAfter: kpiAfter,
                    t0056Total: t0056Obj.total,
                    hasOverrideInLocalStorage: !!storedOverrides['T0056'],
                    finalActive: finalActive,
                    kpiFinal: kpiFinal
                };
            })()"""

            await ws.send(json.dumps({
                "id": 5,
                "method": "Runtime.evaluate",
                "params": {"expression": test_js_4, "returnByValue": True}
            }))

            start = time.time()
            res4 = None
            while time.time() - start < 5:
                msg = json.loads(await ws.recv())
                if msg.get("id") == 5:
                    res4 = msg["result"]["result"]["value"]
                    break
            print("TEST 4 (Cascading Edit & Tab Sync):", res4)

    finally:
        proc.terminate()

if __name__ == "__main__":
    asyncio.run(main())
