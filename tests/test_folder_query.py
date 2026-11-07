import win32com.client
import pythoncom

def test_folder_search():
    pythoncom.CoInitialize()
    conn = win32com.client.Dispatch("ADODB.Connection")
    conn.Open("Provider=Search.CollatorDSO;Extended Properties='Application=Windows';")
    
    # Check folder querying
    # Windows Search has System.Kind = 'folder' or System.ItemType = 'Directory'
    queries = [
        "SELECT TOP 5 System.ItemName, System.ItemPathDisplay, System.ItemType, System.Kind FROM SystemIndex WHERE SCOPE='file:' AND System.ItemName LIKE '%Vibe%'",
        "SELECT TOP 5 System.ItemName, System.ItemPathDisplay, System.ItemType FROM SystemIndex WHERE SCOPE='file:' AND System.Kind = 'folder' AND System.ItemName LIKE '%Code%'"
    ]
    
    for q in queries:
        print("\n--- Testing SQL:", q)
        try:
            rs = win32com.client.Dispatch("ADODB.Recordset")
            rs.Open(q, conn)
            while not rs.EOF:
                name = rs.Fields.Item("System.ItemName").Value
                path = rs.Fields.Item("System.ItemPathDisplay").Value
                itype = rs.Fields.Item("System.ItemType").Value
                print(f"Name: {name} | Path: {path} | Type: {itype}")
                rs.MoveNext()
            rs.Close()
        except Exception as e:
            print("Error:", e)
            
    conn.Close()

if __name__ == "__main__":
    test_folder_search()
