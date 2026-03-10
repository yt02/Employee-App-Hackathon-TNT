$token = az account get-access-token --query accessToken -o tsv
$headers = @{Authorization = "Bearer $token"}
Invoke-RestMethod -Uri "https://tnt-bc5-chatbot-api.scm.azurewebsites.net/api/vfs/site/wwwroot/error.log" -Headers $headers -OutFile "azure_error.log"
