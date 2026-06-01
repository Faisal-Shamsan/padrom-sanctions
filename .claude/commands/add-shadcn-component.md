Add the following shadcn/ui component(s) to the project: $ARGUMENTS

## Install command

Run from the `ui/` directory:

```bash
pnpm dlx shadcn@latest add <component-name>
```

Examples:
```bash
pnpm dlx shadcn@latest add button
pnpm dlx shadcn@latest add form input select badge table
```

You can install multiple components in one command by listing them space-separated.

## Project configuration (already set — do not change)

The project's `ui/components.json` is configured as:

| Setting        | Value              |
|----------------|--------------------|
| Style          | New York           |
| Base color     | Slate              |
| CSS variables  | Yes                |
| Icons          | lucide-react       |
| Path alias `@/`| maps to `ui/` root |

## Where components land

Generated files are placed in `ui/components/ui/`.
**Never hand-edit generated component files.** If you need to customise behaviour,
compose or wrap the component in a new file instead.

## Using components in your code

Always use the `cn()` helper from `lib/utils.ts` for conditional or merged class names:

```typescript
import { cn } from "@/lib/utils";

<Button className={cn("w-full", isLoading && "opacity-50")} />
```

## Styling rules

- Reference design tokens via Tailwind utilities that map to CSS custom properties:
  `bg-primary`, `text-destructive`, `border-muted`, `bg-card`, etc.
- The custom properties (`--primary`, `--destructive`, `--muted`, `--card`, etc.) are
  already defined in `ui/app/globals.css` for both light and dark mode.
- **Do not add new colour values** (hex codes, `rgb()`, etc.) to component files.
  If the existing palette is missing a colour, update `globals.css` with a new CSS
  variable and use it via a Tailwind `@layer` extension — never inline.

## Common components and their use cases

| Component   | When to use                                      |
|-------------|--------------------------------------------------|
| `button`    | Any clickable action                             |
| `form`      | Wrapping React Hook Form fields                  |
| `input`     | Text inputs inside forms                         |
| `select`    | Dropdown selects (e.g. entity type picker)       |
| `badge`     | Status labels (clear / potential_match / etc.)   |
| `table`     | Displaying screening results / match lists       |
| `card`      | Sectioning page content                          |
| `alert`     | Error and warning messages from the API          |
| `skeleton`  | Loading states while queries are in-flight       |
| `separator` | Visual dividers between sections                 |

## Checklist

- [ ] Installed via `pnpm dlx shadcn@latest add <name>` from `ui/`
- [ ] Component file landed in `ui/components/ui/` (not hand-written)
- [ ] `cn()` used for any conditional class logic
- [ ] Only CSS variable-based Tailwind tokens used for colours
- [ ] `pnpm lint` and `pnpm typecheck` pass after adding
