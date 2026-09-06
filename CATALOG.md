# Catalog

One row per **individual component**. This is not a list of assembled apps.

| id | name | provides | files |
|---|---|---|---|
| [`angular-base`](components/angular-base/) | Angular Base | framework | `package.json`, `angular.json`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.spec.json`, `src/index.html`, `src/main.ts`, `src/styles.css`, … (17 files) |
| [`aos`](components/aos/) | Animate On Scroll (AOS) | ui, animation | `types/aos.d.ts`, `lib/aos.ts`, `components/aos-init.tsx` |
| [`aspnet-base`](components/aspnet-base/) | ASP.NET Core Base | backend | `<%= projectName || 'AspNetCoreApp' %>.csproj`, `Program.cs`, `appsettings.json`, `appsettings.Development.json`, `Controllers/ExampleController.cs`, `Models/AppDbContext.cs`, `Models/Example.cs`, `Properties/launchSettings.json`, … (12 files) |
| [`auth0`](components/auth0/) | Auth0 Authentication | authentication | `lib/auth0.ts`, `proxy.ts`, `app/login/page.tsx` |
| [`authjs`](components/authjs/) | Auth.js (NextAuth v5) | authentication | `auth.ts`, `app/api/auth/[...nextauth]/route.ts`, `proxy.ts`, `app/login/page.tsx` |
| [`aws-hosting`](components/aws-hosting/) | AWS Hosting | hosting | `AWS_README.md`, `.ebextensions/nextjs.config` |
| [`azure-hosting`](components/azure-hosting/) | Azure Hosting | hosting | `AZURE_README.md` |
| [`braintree`](components/braintree/) | Braintree Web SDK | payments, billing | `types/braintree-web.d.ts`, `lib/braintree/client.ts`, `lib/braintree/hosted-fields.ts` |
| [`clerk`](components/clerk/) | Clerk Authentication | authentication | `providers.tsx`, `proxy.ts`, `app/sign-in/[[...sign-in]]/page.tsx`, `app/sign-up/[[...sign-up]]/page.tsx`, `app/api/webhooks/clerk/route.ts` |
| [`cloudflare-hosting`](components/cloudflare-hosting/) | Cloudflare Hosting | hosting | `wrangler.toml`, `.wranglerignore`, `CLOUDFLARE_README.md` |
| [`core-js`](components/core-js/) | Core JS Polyfill | polyfill, browser-support | `lib/core-js.ts` |
| [`day-js`](components/day-js/) | Day.js Date Library | date-time, utilities | `lib/dayjs.ts`, `types/dayjs.d.ts` |
| [`django-base`](components/django-base/) | Django Base | backend | `requirements.txt`, `requirements-dev.txt`, `manage.py`, `myproject/settings.py`, `myproject/urls.py`, `myproject/wsgi.py`, `myproject/asgi.py`, `myapp/models.py`, … (17 files) |
| [`express`](components/express/) | Express Backend | backend | `package.json`, `tsconfig.json`, `src/server.ts`, `src/routes/index.ts`, `src/routes/health.ts`, `src/middleware/errorHandler.ts`, `src/middleware/requestLogger.ts`, `src/config/index.ts`, … (13 files) |
| [`fastapi-base`](components/fastapi-base/) | FastAPI Base | backend | `requirements.txt`, `requirements-dev.txt`, `main.py`, `app/__init__.py`, `app/api/__init__.py`, `app/api/v1/__init__.py`, `app/api/v1/endpoints/__init__.py`, `app/api/v1/endpoints/health.py`, … (22 files) |
| [`firebase`](components/firebase/) | Firebase JS SDK | database, authentication, realtime | `lib/firebase.ts` |
| [`footer`](components/footer/) | Footer | footer | `components/footer.tsx` |
| [`gcp-hosting`](components/gcp-hosting/) | Google Cloud Platform Hosting | hosting | `GCP_README.md`, `Dockerfile`, `.dockerignore` |
| [`jquery`](components/jquery/) | jQuery | dom-manipulation, utilities | `lib/jquery.ts` |
| [`laravel-base`](components/laravel-base/) | Laravel Base | backend | `composer.json`, `.env.example`, `.gitignore`, `artisan`, `bootstrap/app.php`, `bootstrap/providers.php`, `config/app.php`, `config/database.php`, … (21 files) |
| [`mongodb`](components/mongodb/) | MongoDB Database | database | `docker-compose.yml`, `.env.example`, `lib/mongodb.ts` |
| [`mysql`](components/mysql/) | MySQL Database | database | `docker-compose.yml`, `.env.example`, `prisma/schema.prisma` |
| [`navbar`](components/navbar/) | Navbar | navigation | `components/navbar.tsx` |
| [`nestjs`](components/nestjs/) | NestJS Backend | backend | `package.json`, `tsconfig.json`, `tsconfig.build.json`, `nest-cli.json`, `src/main.ts`, `src/app.module.ts`, `src/app.controller.ts`, `src/app.service.ts`, … (17 files) |
| [`nextjs-base`](components/nextjs-base/) | Next.js App Router Base | framework | `package.json`, `tsconfig.json`, `next.config.ts`, `next-env.d.ts`, `eslint.config.mjs`, `.gitignore`, `README.md`, `app/layout.tsx`, … (11 files) |
| [`paddle`](components/paddle/) | Paddle Payments | payments, billing | `lib/paddle.ts`, `app/api/checkout/paddle/route.ts`, `app/api/webhooks/paddle/route.ts`, `components/paddle-checkout-button.tsx` |
| [`paypal`](components/paypal/) | PayPal React SDK | payments, billing | `lib/paypal/client.ts`, `components/paypal-provider.tsx`, `components/paypal-buttons.tsx` |
| [`postgres`](components/postgres/) | PostgreSQL | database | `docker-compose.yml`, `.env.example` |
| [`prettier-eslint-config`](components/prettier-eslint-config/) | Prettier + ESLint Config | code-formatting, linting | `.prettierrc.json`, `.prettierignore`, `eslint.config.mjs` |
| [`prisma`](components/prisma/) | Prisma ORM (PostgreSQL) | orm | `prisma/schema.prisma`, `prisma.config.ts`, `lib/prisma.ts` |
| [`railway-hosting`](components/railway-hosting/) | Railway Hosting | hosting | `railway.toml`, `.railwayignore`, `RAILWAY_README.md` |
| [`recaptcha`](components/recaptcha/) | reCAPTCHA Widget | security, captcha | `components/recaptcha-widget.tsx`, `components/recaptcha-script.tsx` |
| [`render-hosting`](components/render-hosting/) | Render Hosting | hosting | `render.yaml`, `.renderignore`, `RENDER_README.md` |
| [`shadcn-ui`](components/shadcn-ui/) | Shadcn UI (Button, Card) | ui-components | `lib/utils.ts`, `components/ui/button.tsx`, `components/ui/card.tsx` |
| [`sqlite`](components/sqlite/) | SQLite Database | database | `.env.example`, `prisma/schema.prisma` |
| [`sqlserver`](components/sqlserver/) | SQL Server Database | database | `docker-compose.yml`, `.env.example` |
| [`stripe`](components/stripe/) | Stripe Checkout | payments, billing | `lib/stripe.ts`, `app/api/checkout/route.ts`, `app/api/webhooks/stripe/route.ts`, `components/checkout-button.tsx` |
| [`supabase-auth-ui`](components/supabase-auth-ui/) | Supabase Auth Pages (Login + Callback) | auth-ui | `app/login/page.tsx`, `app/auth/callback/route.ts` |
| [`supabase-client`](components/supabase-client/) | Supabase Database & Auth Client | database, authentication | `lib/supabase/client.ts`, `lib/supabase/server.ts`, `components/supabase-provider.tsx` |
| [`svelte-base`](components/svelte-base/) | SvelteKit Base | framework | `package.json`, `tsconfig.json`, `svelte.config.js`, `vite.config.ts`, `src/app.html`, `src/app.css`, `src/routes/+page.svelte`, `src/routes/+layout.svelte`, … (12 files) |
| [`swiper`](components/swiper/) | Swiper Slider | ui, carousel, slider | `lib/swiper.ts`, `components/swiper-slider.tsx` |
| [`tailwind`](components/tailwind/) | Tailwind CSS | styling | `postcss.config.mjs`, `app/globals.css` |
| [`vue-base`](components/vue-base/) | Vue Base | framework | `package.json`, `vite.config.ts`, `tsconfig.json`, `tsconfig.node.json`, `tsconfig.app.json`, `index.html`, `src/main.ts`, `src/App.vue`, … (23 files) |
