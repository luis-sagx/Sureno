/// <reference path="../.astro/types.d.ts" />

interface ImportMetaEnv {
  readonly FLASK_API_URL?: string;
}
interface ImportMeta {
  readonly env: ImportMetaEnv;
}
