import resolve from 'rollup-plugin-node-resolve';

module.exports = {
  input: 'cartoframes/assets/src/index.js',
  output: {
    file: 'cartoframes/assets/src/bundle.js',
    format: 'iife',
    name: 'init'
  },
  plugins: [ resolve() ],
  watch: {
    include: [
      'cartoframes/assets/src/**/*.js',
      'cartoframes/assets/**/*.j2'
    ],
    exclude: [
      'node_modules/**',
      'cartoframes/assets/src/bundle.js'
    ]
  }
};
