export type Mode = 'off' | 'lite' | 'full' | 'custom'
export type ToolSettings = { on: boolean } & Record<string, number | boolean>
export type Config = { mode: Mode; tools: Record<string, ToolSettings> }

declare module 'claude-code' {
  interface PluginState {
    'token-diet-panel': { config: Shaped<Config> }
  }
}
