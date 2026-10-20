import time
import win32com.client

def benchmark_persistent():
    conn = win32com.client.Dispatch("ADODB.Connection")
    conn.Open("Provider=Search.CollatorDSO;Extended Properties='Application=Windows';")
    
    queries = ["%python%", "%code%", "%steam%", "%discord%"]
    for q in queries:
        t0 = time.time()
        rs = win32com.client.Dispatch("ADODB.Recordset")
        query = f"SELECT TOP 3 System.ItemName, System.ItemPathDisplay FROM SystemIndex WHERE SCOPE='file:' AND System.ItemName LIKE '{q}'"
        rs.Open(query, conn)
        elapsed = (time.time() - t0) * 1000
        items = []
        while not rs.EOF:
            items.append(rs.Fields.Item("System.ItemName").Value)
            rs.MoveNext()
        rs.Close()
        print(f"Query '{q}' took {elapsed:.2f} ms, found {len(items)} items: {items[:2]}")
        
    conn.Close()

if __name__ == "__main__":
    benchmark_persistent()
