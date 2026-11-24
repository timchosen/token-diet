import { atom, read, update } from 'claude-code'
import type { EngineInterface as Engine, Register } from 'claude-code'

import type { Config, Mode } from '../types'

const PANE = 'token-diet'

type Option = { id: string; label: string; initial: number | boolean; choices?: number[] }
type Tool = { id: string; job: string; isLite: boolean; options: Option[] }

// Mirrors TOOLS in the skill's settings.py: change both together.
const TOOLS: Tool[] = [
  { id: 'trafilatura', job: 'Web pages', isLite: true, options: [{ id: 'links', label: 'Keep links', initial: false }] },
  { id: 'jq', job: 'JSON and API replies', isLite: true, options: [{ id: 'max_rows', label: 'Most rows', initial: 50, choices: [10, 20, 50, 100, 200] }] },
  {
    id: 'ripgrep',
    job: 'Searching files',
    isLite: true,
    options: [
      { id: 'context', label: 'Lines around a match', initial: 2, choices: [0, 1, 2, 3, 5] },
      { id: 'max_matches', label: 'Most matches', initial: 40, choices: [10, 20, 40, 80, 200] },
    ],
  },
  { id: 'duckdb', job: 'Spreadsheets and data files', isLite: true, options: [{ id: 'limit', label: 'Most rows', initial: 20, choices: [10, 20, 50, 100] }] },
  { id: 'docling', job: 'PDFs and Office files', isLite: false, options: [{ id: 'ocr', label: 'Read scanned pages (slow)', initial: false }] },
  { id: 'pagediff', job: 'Pages already read', isLite: false, options: [{ id: 'max_lines', label: 'Most changed lines', initial: 200, choices: [50, 100, 200, 500] }] },
  { id: 'rtk', job: 'Long command output', isLite: false, options: [] },
  { id: 'tenacity', job: 'Calls that sometimes fail', isLite: false, options: [{ id: 'attempts', label: 'Tries', initial: 3, choices: [1, 2, 3, 5] }] },
  { id: 'pydantic', job: 'Checking structured output', isLite: false, options: [] },
]

const MODES: Mode[] = ['off', 'lite', 'full']
const NAME: Record<Mode, string> = { off: 'Off', lite: 'Lite', full: 'Full', custom: 'Custom' }

const preset = (mode: Mode): Config => ({
  mode,
  tools: Object.fromEntries(
    TOOLS.map(tool => [
      tool.id,
      {
        on: mode === 'full' || (mode === 'lite' && tool.isLite),
        ...Object.fromEntries(tool.options.map(option => [option.id, option.initial])),
      },
    ]),
  ),
})

// The file is edited by the settings page and by hand too: keep known keys of the right type, reset the rest.
const clean = (raw: unknown): Config => {
  const given = (typeof raw === 'object' && raw !== null ? raw : {}) as { mode?: unknown; tools?: unknown }
  const tools = (typeof given.tools === 'object' && given.tools !== null ? given.tools : {}) as Record<string, unknown>
  const config = preset('full')
  if (given.mode === 'off' || given.mode === 'lite' || given.mode === 'custom') {
    config.mode = given.mode
  }
  for (const tool of TOOLS) {
    const got = (typeof tools[tool.id] === 'object' && tools[tool.id] !== null ? tools[tool.id] : {}) as Record<string, unknown>
    const mine = config.tools[tool.id]!
    if (typeof got.on === 'boolean') {
      mine.on = got.on
    }
    for (const option of tool.options) {
      const value = got[option.id]
      if (typeof value === typeof option.initial && (typeof value === 'boolean' || Number.isInteger(value))) {
        mine[option.id] = value as number | boolean
      }
    }
  }

  return config
}

const config = atom({ plugin: 'token-diet-panel', key: 'config' } as const, preset('full'), { shape: 'config-1' })

// Installed inside the skill's folder the file sits beside SKILL.md; otherwise it is in the user's skills folder.
const path = async ($: Engine) => {
  if (await $.fs.exists(`${$.plugin.root}/SKILL.md`)) {
    return `${$.plugin.root}/config.json`
  }
  const home = (await $.env.get('HOME')) ?? (await $.env.get('USERPROFILE')) ?? '~'

  return `${home}/.claude/skills/token-diet/config.json`
}

const load = async ($: Engine) => {
  const text = await $.fs.read(await path($)).catch(() => '{}')
  let raw: unknown = {}
  try {
    raw = JSON.parse(text)
  } catch {
    raw = {}
  }
  await update($, config, () => clean(raw))
}

const change = async ($: Engine, edit: (now: Config) => Config) => {
  await update($, config, edit)
  await $.fs.write(await path($), `${JSON.stringify(await read($, config))}\n`)
}

const setMode = ($: Engine, mode: Mode) =>
  change($, now => {
    const next = preset(mode)
    for (const tool of TOOLS) {
      // A mode changes which tools are on; the tuning under each tool is kept.
      next.tools[tool.id] = { ...now.tools[tool.id]!, on: mode === 'off' ? now.tools[tool.id]!.on : next.tools[tool.id]!.on }
    }

    return next
  })

const setTool = ($: Engine, id: string, key: string, value: number | boolean) =>
  change($, now => {
    const tools = Object.fromEntries(
      Object.entries(now.tools).map(([name, tool]) => [
        name,
        // Switching one tool on while Off starts from nothing on, so only that tool is used.
        key === 'on' && now.mode === 'off' ? { ...tool, on: false } : { ...tool },
      ]),
    )
    tools[id] = { ...tools[id]!, [key]: value }

    return { mode: key === 'on' ? 'custom' : now.mode, tools }
  })

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await load($)
    await $.command.register({ name: 'token-diet-settings', description: 'Open the token diet panel: off, lite, full, and each tool' })

    return next(e)
  })

  on('command.run', { command: 'token-diet-settings' }, async $ => {
    await load($)
    await $.ui.open({ id: PANE, title: 'Token diet' })

    return { text: 'Token diet panel opened.' }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey) {
      return next(e)
    }
    const { Box, Button, Text } = $.ui.resolve(e)
    const now = await read($, config)

    return (
      <Box gap={1}>
        <Text dimColor>Token diet{now.mode === 'custom' ? ': Custom' : ''}</Text>
        {MODES.map(mode => (
          <Button
            key={`mode-${mode}`}
            label={NAME[mode]}
            variant={now.mode === mode ? 'primary' : 'secondary'}
            onPress={() => setMode($, mode)}
          />
        ))}
        <Button
          key="tune"
          label="Tune"
          onPress={async () => {
            await load($)
            await $.ui.open({ id: PANE, title: 'Token diet' })
          }}
        />
      </Box>
    )
  })

  on('ui.render', { component: 'Pane', requestId: PANE }, async ($, e) => {
    const { Box, Button, Select, Text } = $.ui.resolve(e)
    const now = await read($, config)
    const isOff = now.mode === 'off'

    return (
      <Box flexDirection="column" gap={1}>
        <Box gap={1}>
          <Text bold>Mode: {NAME[now.mode]}</Text>
          {MODES.map(mode => (
            <Button
              key={`pane-mode-${mode}`}
              label={NAME[mode]}
              variant={now.mode === mode ? 'primary' : 'secondary'}
              onPress={() => setMode($, mode)}
            />
          ))}
        </Box>
        {TOOLS.map(tool => {
          const mine = now.tools[tool.id]!
          const isOn = mine.on && !isOff

          return (
            <Box flexDirection="column">
              <Box gap={1}>
                <Button
                  key={`on-${tool.id}`}
                  label={isOn ? 'On' : 'Off'}
                  variant={isOn ? 'primary' : 'secondary'}
                  onPress={() => setTool($, tool.id, 'on', !isOn)}
                />
                <Text dimColor={!isOn}>
                  {tool.job} ({tool.id})
                </Text>
              </Box>
              {isOn &&
                tool.options.map(option =>
                  option.choices === undefined ? (
                    <Box gap={1}>
                      <Button
                        key={`${tool.id}-${option.id}`}
                        label={mine[option.id] === true ? 'Yes' : 'No'}
                        onPress={() => setTool($, tool.id, option.id, mine[option.id] !== true)}
                      />
                      <Text dimColor>{option.label}</Text>
                    </Box>
                  ) : (
                    <Select
                      key={`${tool.id}-${option.id}`}
                      label={option.label}
                      value={String(mine[option.id])}
                      options={[...new Set([...option.choices, Number(mine[option.id])])]
                        .sort((a, b) => a - b)
                        .map(choice => ({ value: String(choice) }))}
                      onSelect={value => setTool($, tool.id, option.id, Number(value))}
                    />
                  ),
                )}
            </Box>
          )
        })}
      </Box>
    )
  })
}
