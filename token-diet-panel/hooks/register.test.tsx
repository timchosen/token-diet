import { expect, test } from 'claude-code/testing'

const PANE = {
  plugin: 'token-diet-panel',
  component: 'Pane',
  requestId: 'token-diet',
  props: { title: 'Token diet', isFocused: false, bodyColumns: 60, placement: 'dock', scroll: { offset: 0, bodyRows: 40 }, view: {} },
} as const

test('Lite keeps four tools on and writes the file; one switch makes it Custom', async ($, on) => {
  const written: string[] = []
  on('fs.exists', () => ({ value: true }))
  on('fs.read', () => ({ value: '{"mode":"nope","tools":{"jq":{"on":true,"max_rows":"x"}}}' }))
  on('fs.write', (_, e) => {
    written.push(e.text)

    return { value: undefined }
  })
  on('command.register', () => ({ value: { command: 'token-diet-settings' } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))

  await $.session.start({ cwd: '/', surface: 'desktop', isInteractive: true })

  const ui = await $.ui.mount({ ...PANE, surface: 'desktop' })
  // A bad mode and a bad number in the file fall back to Full and the default.
  expect((await ui.find({ type: 'Text', text: /Mode/ }))?.text).toBe('Mode: Full')

  await ui.press({ key: 'pane-mode-lite' })
  const lite = JSON.parse(written.at(-1)!)
  expect(lite.mode).toBe('lite')
  expect(Object.keys(lite.tools).filter(id => lite.tools[id].on)).toEqual(['trafilatura', 'jq', 'ripgrep', 'duckdb'])
  expect(lite.tools.jq.max_rows).toBe(50)

  await ui.press({ key: 'on-ripgrep' })
  const custom = JSON.parse(written.at(-1)!)
  expect(custom.mode).toBe('custom')
  expect(custom.tools.ripgrep.on).toBe(false)

  await ui.press({ key: 'pane-mode-off' })
  expect(JSON.parse(written.at(-1)!).mode).toBe('off')
  await ui.unmount()
})
