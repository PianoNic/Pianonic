# Helpful Stuff

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

---

## ASP.NET Core & EF Core Setup

### Create a New ASP.NET Core Project
```sh
dotnet new webapi -n MyApi
cd MyApi
```

### Add EF Core
```sh
dotnet add package Microsoft.EntityFrameworkCore.SqlServer
```

### Create a Model
```csharp
public class Product
{
    public int Id { get; set; }
    public string Name { get; set; }
}
```

### Create a DbContext
```csharp
public class AppDbContext : DbContext
{
    public DbSet<Product> Products { get; set; }

    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }
}
```

### Configure Database in `appsettings.json`
```json
"ConnectionStrings": {
  "DefaultConnection": "Server=.;Database=MyDatabase;Trusted_Connection=True;"
}
```

### Register DbContext in `Program.cs`
```csharp
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));
```

### Apply Migrations
```sh
dotnet ef migrations add InitialCreate
```
```sh
dotnet ef database update
```

### Create a Controller
```csharp
[Route("api/[controller]")]
[ApiController]
public class ProductsController : ControllerBase
{
    private readonly AppDbContext _context;

    public ProductsController(AppDbContext context)
    {
        _context = context;
    }

    [HttpGet]
    public async Task<IEnumerable<Product>> Get()
    {
        return await _context.Products.ToListAsync();
    }
}
```
