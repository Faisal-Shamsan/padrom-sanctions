import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * shadcn/ui utility — merges Tailwind classes safely.
 * Use this instead of string concatenation to avoid class conflicts
 * (e.g. `cn("p-4", conditional && "p-8")` correctly resolves to `p-8`).
 */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}
