## ng-openapi-gen Setup (Angular)

### Install ng-openapi-gen
```sh
npm install ng-openapi-gen --save-dev
```

### Generate API Client
1. Ensure you have an OpenAPI JSON file (e.g., `swagger.json`).
2. Add configuration in `ng-openapi-gen.json`:
   ```json
   {
     "input": "swagger.json",
     "output": "src/app/api"
   }
   ```
3. Run the generator:
   ```sh
   npx ng-openapi-gen
   ```
4. Import services from `src/app/api` and use them in your Angular components.