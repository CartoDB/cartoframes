import { parse } from './parse';

export function displayError(e) {
  const error$ = document.getElementById('error-container');
  const errors$ = error$.getElementsByClassName('errors');
  const stacktrace$ = document.getElementById('error-stacktrace');

  errors$[0].innerHTML = e.name;
  errors$[1].innerHTML = e.type;
  errors$[2].innerHTML = e.message.replace(e.type, '');

  error$.style.visibility = 'visible';

  const stack = parse(e.stack);
  const list = stack.map(item => {
    return `<li>
      at <span class="stacktrace-method">${item.methodName}:</span>
      (${item.file}:${item.lineNumber}:${item.column})
    </li>`;
  });

  stacktrace$.innerHTML = list.join('\n');
}