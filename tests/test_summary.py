import win32com.client
import pythoncom

def test_summary():
    pythoncom.CoInitialize()
    conn = win32com.client.Dispatch("ADODB.Connection")
    conn.Open("Provider=Search.CollatorDSO;Extended Properties='Application=Windows';")
    
    sql = "SELECT TOP 3 System.ItemName, System.ItemPathDisplay, System.Search.AutoSummary FROM SystemIndex WHERE SCOPE='file:' AND FREETEXT(System.Search.Contents, 'python')"
    try:
        rs = win32com.client.Dispatch("ADODB.Recordset")
        rs.Open(sql, conn)
        while not rs.EOF:
            name = rs.Fields.Item("System.ItemName").Value
            summary = rs.Fields.Item("System.Search.AutoSummary").Value
            print(f"Name: {name} | Summary: {summary}")
            rs.MoveNext()
        rs.Close()
    except Exception as e:
        print("Error with AutoSummary:", e)
    conn.Close()

if __name__ == "__main__":
    test_summary()
