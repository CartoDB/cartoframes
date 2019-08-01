import resolve from 'rollup-plugin-node-resolve';

module.exports = {
  input: 'cartoframes/assets/templates/src/index.js',
  output: {
    file: 'cartoframes/assets/templates/src/bundle.js',
    format: 'iife',
    name: 'init'
  },
  plugins: [ resolve() ],
  watch: {
    include: [
      'cartoframes/assets/templates/src/**/*.js',
      'cartoframes/assets/templates/**/*.j2'
    ],
    exclude: [
      'node_modules/**',
      'cartoframes/assets/templates/src/bundle.js'
    ]
  }
};