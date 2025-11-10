// @ts-check
import { antfu } from '@antfu/eslint-config'
import perfectionist from 'eslint-plugin-perfectionist'

import withNuxt from './.nuxt/eslint.config.mjs'

const perfectionistNatural = perfectionist.configs['recommended-natural']

export default withNuxt(
  antfu({
    rules: {
      'perfectionist/sort-imports': perfectionistNatural.rules?.['perfectionist/sort-imports'],
      'perfectionist/sort-exports': perfectionistNatural.rules?.['perfectionist/sort-exports'],
      'perfectionist/sort-named-imports': perfectionistNatural.rules?.['perfectionist/sort-named-imports'],
      'perfectionist/sort-named-exports': perfectionistNatural.rules?.['perfectionist/sort-named-exports'],
    },
    ignores: [
      'CLAUDE.md',
    ],
  }),
)
