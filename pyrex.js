const ρσ_kwargs_symbol = (typeof Symbol === "function") ? Symbol.for("kwargs-object") : "kwargs-object-Symbol-5d0927e5554349048cf0e3762a228256";

function isJSON(object) {
  if (typeof object === 'object' && object !== null) {
    if (typeof Object.getPrototypeOf === 'function') {
      const prototype = Object.getPrototypeOf(object);
      return prototype === Object.prototype || prototype === null;
    }
    else {
      return Object.prototype.toString.call(object) === '[object Object]';
    }
  }
  return false;
}

function wrap (component) {
  function plain_wrapper(props, ...children) {
    if ((props && window.Symbol && Symbol.for('react.element') === props['$$typeof']) || !isJSON(props) || props.constructor === undefined) {
      const new_children = !Array.isArray(props) ? [props] : props;
      if (!children.length) children = new_children;
      else children = new_children.concat(children);
      props = {};
    }
    return create_component(props, children);
  }
  function rapydscript_wrapper() {
    var kwargs;
    var props = arguments[arguments.length-1];
    if (props && props.hasOwnProperty('__kwargtrans__')) {
      //if (props.children) kwargs_children = props.children;
      //else ;
      kwargs = props;
    }
    if (props === null || typeof props !== "object" || props [ρσ_kwargs_symbol] !== true) props = {};
    var children = Array.prototype.slice.call(arguments, 0);
    if (kwargs) props = kwargs;
    if (props !== null && typeof props === "object" && props [ρσ_kwargs_symbol] === true) children.pop();
    if (props.children) children.push(...props.children);
    return create_component(props, children);
  }
  function create_component(props, children) {
    for (let key in props) {
      if (key.startsWith('data_')) {
        props[key.replace('data_', 'data-')] = props[key];
        delete props[key];
      }
    }
    const current_component = (component && typeof component === 'object' && component.default) ? component.default : component;
    if (!children.length) return require('react').createElement(current_component, {...props});
    return require('react').createElement(current_component, {...props}, children);
  }
  function wrapper (...args) {
    if (!args.find((arg) => arg && typeof arg === 'object' && (arg[ρσ_kwargs_symbol] === true || arg.hasOwnProperty('__kwargtrans__')))) return plain_wrapper(...args);
    return rapydscript_wrapper(...args);
  }
  return wrapper;
}

function kwargs (module, ...keywords) {
  return keywords.flat().map(keyword => module[keyword]);
}

function pyrex (...components) {
  components = components.flat();
  if (components.length === 1) return wrap(components[0]);
  return components.map(wrap);
}

pyrex.wrap = wrap;
pyrex.component = pyrex;
pyrex.kwargs = kwargs;

module.exports = pyrex;
