from types import ClassType
from javascript import JSON, Object, Function, function, types, run_javascript, asynchronous
from .constructor import *

def create_promise():
    object = Object.get('window')['Object'].new()
    promise = Object.get('window')['Promise'].new(Object.createClosure(create_promise_handle, object).toRef())
    return promise, object['resolve']

@Function
def create_promise_handle(args):
    assert args is not None and len(args) >= 2
    object = args[0]
    object['resolve'] = args[1].toRef()

def component_from_object(object):
    component = ReactComponent()
    component.component_object = object
    return component

custom_component_count = 0

def create_custom_component(Component, State, Props=None, Pure=False):
    global custom_component_count
    custom_component_count += 1
    custom_count = custom_component_count
    class_def = Component
    constructor = True if hasattr(class_def, 'constructor') else False
    custom_mount = class_def.mount != ReactComponent.mount
    custom_mount_async = hasattr(class_def.mount, 'asynchronous')
    #custom_unmount = class_def.unmount != ReactComponent.unmount unmount shouldn't call setState
    custom_update = class_def.update != ReactComponent.update
    custom_update_async = hasattr(class_def.update, 'asynchronous')
    if not constructor:
       def __init__(self, children=None, props={}, react_props=None):
           self.children = children
           self.native_props = props or {}
           self.props = react_props
           self.state = State()
       def init_constructor(self):
           return
       class_def.__init__  = __init__
       class_def.init_constructor = init_constructor
    if constructor:
       #if class_def.constructor.__code__.co_argcount == 0:
          def __init__(self, children=None, props={}, react_props=None):
              self.children = children
              self.native_props = props or {}
              self.props = react_props
              self.state = State()
              if react_props is not None: self.constructor()
          def init_constructor(self):
              self.constructor()
          class_def.__init__  = __init__
          class_def.init_constructor = init_constructor
          """else:
          class Args: pass
          def init_rpython_component(self, children=None, props={}, react_props=None):
              self.children = children
              self.native_props = props or {}
              self.props = react_props
              self.state = State()
              if react_props is None: self.rpython_args = Args()
              #elif self.props['rpython_cache_id'].type != 'undefined':
              else: self.rpython_args = self.rpython_caches[self.props['rpython_cache_id'].toString()].rpython_args
          class_def.init_rpython_component  = init_rpython_component
          args = [arg for arg in class_def.constructor.__code__.co_varnames if arg != 'self']
          defaults = class_def.constructor.__defaults__
          namespace = {key: value for key,value in zip(args, defaults)}
          indent = '\n' + (' ' * 4)
          code = 'def __init__(self, children=None, props={}, react_props=None, ' + ', '.join(arg + '=' + arg for arg in args) + '):'
          code += indent + 'self.init_rpython_component(children=children, props=props, react_props=react_props)'
          code += indent + 'if react_props is None: ' + ', '.join('self.rpython_args.' + arg  for arg in args) + ' = ' + ', '.join(arg for arg in args)
          code += indent + 'else: self.constructor(' + ', '.join(arg + '=self.rpython_args.' + arg for arg in args) + ')'
          exec(code, namespace)
          class_def.__init__ = namespace['__init__']"""
    #def create_component(children=None, props={}):
    #    component = Component(children=children, props=props) #.render
        #component.component = name
    #    component.function[0] = entry
    #    return component
    class Cache:

        cache = None

        def __getitem__(self, key):
            return self.cache[key]

        def __setitem__(self, key, value):
            if self.cache is None: self.cache = {}
            self.cache[key] = value
    Original = Component
    mount_wait = None
    if custom_mount_async:
       @asynchronous
       def mount_wait(mount, state):
           mount.wait()
           Object.get('Module')['rpython_react_state_event'] = None
    @function
    def mount(function, props):
        component = Original (children=[component_from_object(children) for children in props['children'].toArray()] if props['children'].type == 'array' else [component_from_object(props['children'])] if props['children'].type == 'object' else [], react_props=props)
        state = component.state
        object_cache[Component][props['rpython_cache_id'].toString()] = component
        if custom_mount:
           component.state_function = function
        if custom_mount_async:
           Object.get('Module')['rpython_react_state_event'] = JSON.fromInteger(0)
           function.keep()
           mount_wait(component.mount(), state)
           return
        Object.get('Module')['rpython_react_state_event'] = JSON.fromInteger(0)
        component.mount()
        Object.get('Module')['rpython_react_state_event'] = None
        #id = object.toInteger()
        #if id in caches:
        #   caches[id].mount()
    @function
    def update(function, props):
        component = Original (children=[component_from_object(children) for children in props['children'].toArray()] if props['children'].type == 'array' else [component_from_object(props['children'])] if props['children'].type == 'object' else [], react_props=props)
        if custom_update:
           component.state_function = function
           if custom_update_async:
              Object.get('Module')['rpython_react_state_event'] = JSON.fromInteger(0)
              function.keep()
        component.update()
        #id = object.toInteger()
        #if id in caches:
        #   caches[id].update()
    @function
    def unmount(object, props):
        component = Original (children=[component_from_object(children) for children in props['children'].toArray()] if props['children'].type == 'array' else [component_from_object(props['children'])] if props['children'].type == 'object' else [], react_props=props)
        component.unmount()
        #id = object.toInteger()
        #if id in caches:
        #   caches[id].unmount()
        #   caches[id].clean()
    @function
    def use_state(state_function, props):
        Date = Object.get('window', 'Date')
        state_function.call(Date['now'].call().toRef())
        #props['rpython_component_id'] = str(custom_count)
        return Object.fromDict({'rpython_component_id': str(custom_count), 'rpython_cache_id': props['rpython_cache_id'].toRef()})
    @function
    def use_effect(id, effect, props):
        effect.call(id.toRef(), props.toRef())
    @function
    def use_effect_cleanup(id, props):
        return Object.createClosure(unmount, id, props)
    @function
    def entry(props):
        #variable = "rpython_react_component_count_" + str(custom_component_count)
        #globals = Object.get('global')
        #if globals[variable].type == 'undefined':
        #   globals[variable] = JSON.fromInteger(-1)
        #run_javascript("!('%s' in global) && (global.%s = -1)" % (variable, variable))
        useState = Object.get('window', 'React', 'useState').toFunction()
        state = useState(JSON.fromInteger(0))
        function = Object.createClosure(use_state, state['1'], props) #.keep()
        #object = Object("window.React.useState(function() {return {step: 0, id: ++global.%s}}).map(function (value, index, values) {return typeof value !== 'function' ? value : function () {return value({...values[0], step: values[0].step + 1})}})" % (variable))
        #state, function = object['0'], object['1'].keep() #toFunction()
        #step, id = state['step'].toInteger(), state['id']
        #if functions.mount is None: functions.mount = JSON.fromFunction(mount)
        #if functions.update is None: functions.update = JSON.fromFunction(update)
        #if functions.unmount is None: functions.unmount = JSON.fromFunction(unmount)
        step = state['0'].toInteger()
        id = props['rpython_cache_id']
        useEffect = Object.get('window', 'React', 'useEffect').toFunction()
        effect = Object.createClosure(use_effect, function, Object.fromFunction(mount) if step == 0 else Object.fromFunction(update), props)
        useEffect(effect.toRef())
        cleanup = Object.createClosure(use_effect_cleanup, id, props)
        useEffect(cleanup.toRef(), JSON.fromList([]))
        is_state_event = Object.get('Module', 'rpython_react_state_event').type not in ['undefined', 'null']
        component = Original (children=[component_from_object(children) for children in props['children'].toArray()] if props['children'].type == 'array' else [component_from_object(props['children'])] if props['children'].type == 'object' else [], react_props=props) if not is_state_event else object_cache[Component][id.toString()]
        object_cache[Component][id.toString()] = component
        component.props = props
        if is_state_event:
           component.init_constructor()
           component.state_function.release()
           Object.get('Module')['rpython_react_state_event'] = None
        #if step == 0:
           #cleanup = Object.createClosure(use_effect_cleanup, id)
           #useEffect(cleanup.toRef(), JSON.fromList([]))
        #caches[id.toInteger()] = component
        component.state_function = function #.keep()
        #else:
        #   old_function = caches[id.toInteger()].state_function
        #   Object.get('global')[old_function.variable] = function.toRef()
        #if 'mount' in functions and 'update' in functions and 'unmount' in functions:
        #effect = Object("function (effect, cleanup) {return function () {effect(%s)}}" % (id.toString())).call(JSON.fromFunction(mount) if step == 0 else JSON.fromFunction(update))
        #Object('window.React.useEffect').call(effect.toRef())
        #if step == 0:
           #cleanup = Object("function (cleanup) {return function () {return function () {cleanup(%s)}}}" % (id.toString())).call(JSON.fromFunction(unmount))
           #Object('window.React.useEffect').call(cleanup.toRef(), JSON.fromList([]))
           #useEffect(cleanup.toRef())
        #component = caches[id.toInteger()]
        #component.state_function = function
        return component.render().entry()
    entry.function_module = Original.__module__
    Component.entry_function = (entry,)
    #Component.rpython_count = {'count': 0}
    #Component.rpython_caches = {}
    Component.pure_component = Pure
    if Props and any(not prop.startswith('_') for prop in vars(Props)):
       Component = ComponentDecorator(class_def=Props, path='null', component_entry=entry, component_class=Component)
       object_cache[Component] = Cache() #{}
       return Component
    #for key in Component.__dict__: This doesn't work, maybe wrap every custom component regardless of it have Props class or not
    #    setattr(Component, key, getattr(Component, key))
    object_cache[Component] = Cache() #{}
    Component.Component = Component
    return Component

def is_type(value, type):
    if value == type: return True
    if isinstance(value, type): return True
    return False

def Component(class_def=None, path=None, component_entry=None, component_class=None, State=None, Props=None, Pure=False):
    if (State or Props or Pure) and class_def is None:
       if not State:
          class State: pass
       def wrapper(class_def):
           if not issubclass(class_def, ReactComponent):
              namespace = {'ReactRPythonComponent': ReactComponent}
              exec('class ' + class_def.__name__ + '(ReactRPythonComponent): pass', namespace)
              new_class = namespace[class_def.__name__]
              new_class.__dict__ = class_def.__dict__
              class_def = new_class
           return create_custom_component(class_def, State, Props, Pure=Pure)
       return wrapper
    if class_def is None and path:
       def wrapper(class_def):
           return Component(class_def=class_def, path=path)
       return wrapper
    if State is None and class_def and isinstance(class_def, (type, ClassType)) and issubclass(class_def, ReactComponent):
       class State: pass
       return create_custom_component(class_def, State, Props, Pure=Pure)
    name = class_def.__name__ if not component_class else component_class.__name__
    props = {prop: getattr(class_def, prop) for prop in vars(class_def) if not prop.startswith('_')}
    indent = '\n' + (' ' * 4)
    json_props = ', '.join(["'{0}': {1} ".format(prop, '{0} if {0} is not None else "RPYJSON:null:RPYJSON"'.format(prop) if is_type(props[prop], types.str) else 'JSON.fromInt(%s)' % prop if is_type(props[prop], types.int) else 'JSON.fromFloat(%s)' % prop if is_type(props[prop], types.float) else 'JSON.fromBool(%s)' % prop if is_type(props[prop], types.bool) else 'JSON.fromList(%s)' % prop if is_type(props[prop], types.list) else 'JSON.fromTuple(%s)' % prop if is_type(props[prop], types.tuple) else prop + '.toRef()' if is_type(props[prop], Object) else 'JSON.fromFunction(%s)' % prop if is_type(props[prop], types.function) or is_type(props[prop], types.instancemethod) else 'JSON.fromDict(%s)' % prop if is_type(props[prop], types.dict) else 'None') for prop in props])
    code = 'def ' + name + '(children=None, props=None' + (' ,' if props else "") + ', '.join([prop + '=' + prop for prop in props]) + '):'
    code += indent + "rpython_props = {%s}" % (json_props)
    #code += indent + "assert isinstance(children, list), 'The component first argument (children) should be a list of ReactComponent (use keyword argument to add verbosity)'"
    #code += indent + "if not isinstance(props, dict): raise Exception('The component second argument (props) should be a dictionary (use keyword argument to add verbosity)')"
    code += indent + "if props is not None:\n"
    code += ('    ' * 4 * 2) + "for key in props:\n"
    code += ('    ' * 4 * 3) + "if key not in rpython_props or JSON.isFalse(rpython_props[key]): rpython_props[key] = props[key]"
    code += indent + "rpython_component = RPYVARS['Component'](children=children, props=rpython_props)"
    if not component_entry: code += indent + "rpython_component.component = RPYVARS['name']"
    else: code += indent + "rpython_component.entry_function = (RPYVARS['entry'],)"
    code += indent + "return rpython_component"
    #code += indent + "createElement = RPYVARS['Object']('window.React.createElement')"
    #code += indent + "if children is None or not children: return createElement.call(RPYVARS['name'], JSON.fromDict(rpython_props))"
    #code += indent + "return createElement.call(RPYVARS['name'], JSON.fromDict(rpython_props), JSON.fromList([None if object is None else object.toRef() for object in children]))"
    known_types = [str, int, float, dict, list, tuple, bool]
    for prop in props:
        props[prop] = props[prop]() if props[prop] in known_types else props[prop] if type(props[prop]) in known_types else None
    props.update({'RPYVARS': {'Object': Object, 'name': name if path is None else 'RPYJSON:' + path + ':RPYJSON', 'Component': ReactComponent, 'entry': component_entry}, 'JSON': JSON, 'rpytypes': types})
    exec(code, props)
    if component_class:
       for key in component_class.__dict__:
           setattr(props[name], key, getattr(component_class, key))
       props[name].Component = component_class
    return props[name]

ComponentDecorator = Component
