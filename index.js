const ρσ_kwargs_symbol = (typeof Symbol === "function") ? Symbol.for("kwargs-object") : "kwargs-object-Symbol-5d0927e5554349048cf0e3762a228256";

export function wrap (component) {
  function plain_wrapper(props, ...children) {
    if (!isJSON(props) || props.constructor === undefined) {
      const new_children = !Array.isArray(props) ? [props] : props;
      if (!children.length) children = new_children;
      else children = new_children.concat(children);
      props = {};
    }
    return create_component(props, children);
  }
  function rapydscript_wrapper() {
    var props = arguments[arguments.length-1];
    if (props === null || typeof props !== "object" || props [ρσ_kwargs_symbol] !== true) props = {};
    var children = Array.prototype.slice.call(arguments, 0);
    if (props !== null && typeof props === "object" && props [ρσ_kwargs_symbol] === true) children.pop();
    if (props.children) children = props.children;
    return create_component(props, children);
  }
  function create_component(props, children) {
    for (let key in props) {
      if (key.startsWith('data_')) {
        props[key.replace('data_', 'data-')] = props[key];
        delete props[key];
      }
    }
    if (!children.length) return require('react').createElement(component, {...props});
    return require('react').createElement(component, {...props}, children);
  }
  function wrapper (...args) {
    if (!args.find((arg) => arg && typeof arg === 'object' && arg[ρσ_kwargs_symbol] === true)) return plain_wrapper(...args);
    return rapydscript_wrapper(...args);
  }
  return wrapper;
}

export default function pyrex (...components) {
  if (components.length === 1) return wrap(components[0]);
  return components.map(wrap);
}

pyrex.wrap = wrap;