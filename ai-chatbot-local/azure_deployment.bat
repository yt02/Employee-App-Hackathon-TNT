@echo off
setlocal

:: Configuration
set RESOURCE_GROUP=TNT-RG
set LOCATION=malaysiawest
set APP_SERVICE_PLAN=tnt-bc5-plan
set WEB_APP_NAME=tnt-bc5-chatbot-api
set DB_SERVER_NAME=tnt-bc5-chatbot-db
set DB_USER=adminuser
set DB_PASSWORD=SecretPassword123!
set DB_NAME=chatbotdb
set CONNECTION_STRING=eastus2.api.azureml.ms;96c8b907-d749-4dec-8c2a-51a334b457bf;TNT-RG;tnt-bc5-employee-app

echo Using existing Resource Group...
:: call az group create --name %RESOURCE_GROUP% --location %LOCATION%

echo Creating Azure Database for PostgreSQL Flexible Server (this might take a few minutes)...
call az postgres flexible-server create --resource-group %RESOURCE_GROUP% --name %DB_SERVER_NAME% --location %LOCATION% --admin-user %DB_USER% --admin-password "%DB_PASSWORD%" --sku-name Standard_B1ms --tier Burstable --public-access 0.0.0.0 --version 14 --yes

echo Creating database on the Postgres server...
call az postgres flexible-server db create --resource-group %RESOURCE_GROUP% --server-name %DB_SERVER_NAME% --database-name %DB_NAME%

echo Creating App Service Plan...
call az appservice plan create --name %APP_SERVICE_PLAN% --resource-group %RESOURCE_GROUP% --is-linux --location %LOCATION% --sku B1

echo Creating Web App...
call az webapp create --resource-group %RESOURCE_GROUP% --plan %APP_SERVICE_PLAN% --name %WEB_APP_NAME% --runtime "PYTHON:3.10"

echo Configuring App Settings and enabling Oryx build BEFORE deploying...
set DATABASE_URL=postgresql://%DB_USER%:%DB_PASSWORD%@%DB_SERVER_NAME%.postgres.database.azure.com:5432/%DB_NAME%
call az webapp config appsettings set --resource-group %RESOURCE_GROUP% --name %WEB_APP_NAME% --settings AZURE_CONNECTION_STRING="%CONNECTION_STRING%" DATABASE_URL="%DATABASE_URL%" WEBSITES_CONTAINER_START_TIME_LIMIT=1800 WEBSITES_PORT=8000 SCM_DO_BUILD_DURING_DEPLOYMENT=true ENABLE_ORYX_BUILD=true WEBSITE_RUN_FROM_PACKAGE=0

echo Configuring Startup Command...
call az webapp config set --resource-group %RESOURCE_GROUP% --name %WEB_APP_NAME% --startup-file "python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo Creating zip package for deployment...
cd /d "%~dp0"
if exist deploy.zip del deploy.zip
python build_zip.py
if errorlevel 1 (
  echo Failed to create deploy.zip
  exit /b 1
)

echo Deploying zip to Azure App Service with clean publish (forces fresh Oryx artifacts)...
call az webapp deploy --resource-group %RESOURCE_GROUP% --name %WEB_APP_NAME% --src-path deploy.zip --type zip --clean true --restart true

echo Cleaning up zip...
if exist deploy.zip del deploy.zip

echo Fetching the API URL...
call az webapp show --resource-group %RESOURCE_GROUP% --name %WEB_APP_NAME% --query defaultHostName -o tsv

echo Deployment Completed. To initialize the database, please set the DATABASE_URL environment variable locally and run 'python migrate_to_postgres.py'.
endlocal
