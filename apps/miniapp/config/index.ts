import { defineConfig, type UserConfigExport } from '@tarojs/cli'

export default defineConfig(async () => {
  const config: UserConfigExport = {
    projectName: 'heaver-energy-miniapp',
    date: '2026-06-11',
    designWidth: 750,
    sourceRoot: 'src',
    outputRoot: 'dist',
    framework: 'react',
    compiler: 'webpack5',
    mini: {},
    h5: {}
  }

  return config
})

