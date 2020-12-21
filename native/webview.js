var React = {};
var elements = {};
var count = 0;

React.useState = function () {
  if (!React._useState) return;
  return React._useState.apply(this, arguments);
}

React.useEffect = function () {
  if (!React._useEffect) return;
  return React._useEffect.apply(this, arguments);
}

function resetStates() {
  if (React._timer) return;
  React._timer = setTimeout(function () {
    delete React._useState;
    delete React._useEffect;
    delete React._timer;
  }, 0);
}

React.createElement = function (component, props, children) {
  var element = {'component': component, 'props': props};
  if (children) element.children = children;
  if (typeof component === 'function') {
    count += 1;
    element.effects = [];
    React._useState = function (state) {
      //count += 1;
      elements[count] = {'element': element, 'state': state};
      element.id = count;
      function setState(state) {
        element.effects = [];
        React._useState = function () {
          //function inceptionSetState() {
          //}
          return [state, setState];
        }
        React._useEffect = function (...args) {
          element.effects.push(args);
        }
        element.component = component(props);
        resetStates();
        updateElement(count, element);
      }
      return [state, setState];
    }
    React._useEffect = function (...args) {
      element.effects.push(args);
    }
    element.component = component(props);
    resetStates();
  }
  return element;
}

function updateElement(id, element) {
  window.ReactNativeWebView.postMessage(JSON.stringify({type: 'update', id: id, element: element}));
}

window.React = React;
