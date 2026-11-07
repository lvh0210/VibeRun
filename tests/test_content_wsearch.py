import time
import win32com.client
import pythoncom

def test_content_search(keyword="viberun"):
    pythoncom.CoInitialize()
    conn = win32com.client.Dispatch("ADODB.Connection")
    conn.Open("Provider=Search.CollatorDSO;Extended Properties='Application=Windows';")
    
    # Try querying System.Search.Contents
    sql = f"SELECT TOP 5 System.ItemName, System.ItemPathDisplay FROM SystemIndex WHERE SCOPE='file:' AND FREETEXT(System.Search.Contents, '{keyword}')"
    print("Testing SQL:", sql)
    t0 = time.time()
    try:
        rs = win32com.client.Dispatch("ADODB.Recordset")
        rs.Open(sql, conn)
        elapsed = (time.time() - t0) * 1000
        print(f"Content search query finished in {elapsed:.2f} ms")
        while not rs.EOF:
            print("Found:", rs.Fields.Item("System.ItemName").Value, "->", rs.Fields.Item("System.ItemPathDisplay").Value)
            rs.MoveNext()
        rs.Close()
    except Exception as e:
        print("Error with FREETEXT:", e)
        
    conn.Close()

if __name__ == "__main__":
    test_content_search("python")
