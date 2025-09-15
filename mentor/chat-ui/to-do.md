# Frontend Migration To-Do

## Current Status
- Frontend code is currently mixed in with Python backend in `tradehabit-backend/mentor/chat-ui/`
- Need to move to separate frontend repository

## What to Move (Source Code Only)
- `src/` - React components and pages
- `public/` - Static assets
- `package.json` - Dependencies and scripts
- `next.config.js` - Next.js configuration
- `tsconfig.json` - TypeScript configuration
- `.gitignore` - Git ignore rules
- `README.md` - Documentation
- `next-env.d.ts` - Next.js TypeScript definitions

## What NOT to Move (Generated Files)
- `node_modules/` - Will be recreated with `npm install`
- `.next/` - Will be rebuilt with `npm run dev` or `npm run build`
- `.DS_Store` - System files

## Migration Steps
1. Create new frontend repository
2. Copy only source files (see "What to Move" above)
3. In new repo, run:
   ```bash
   npm install    # Recreates node_modules/
   npm run dev    # Rebuilds .next/
   ```
4. Update any API endpoints to point to backend
5. Test functionality
6. Remove `mentor/chat-ui/` from backend repo

## Best Practice Structure
```
my-frontend-project/
├── src/                     # Source code
│   ├── components/
│   ├── pages/
│   └── lib/
├── public/                  # Static assets
├── package.json             # Dependencies
├── next.config.js          # Configuration
├── .gitignore              # Excludes build artifacts
├── README.md
└── .env.local              # Environment variables

# These are generated/installed, NOT in source control:
├── node_modules/           # Installed dependencies
└── .next/                  # Build output
```

## Why This Matters
- **`node_modules/`** - Contains installed packages, should never be committed
- **`.next/`** - Contains build output, should never be committed
- Keeps source code clean and follows industry best practices
- Enables proper separation of concerns between frontend and backend
