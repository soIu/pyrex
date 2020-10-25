from javascript import JSON, Object, types, function, run_javascript

custom_component_count = 0

def create_custom_component(Component, State):
    global custom_component_count
    custom_component_count += 1
    class_def = Component
    constructor = True if hasattr(class_def, 'constructor') else False
    if not constructor:
       def __init__(self, children=None, props={}, react_props=None):
           self.children = children
           self.native_props = props or {}
           self.props = react_props
           self.state = State()
       class_def.__init__  = __init__
    if constructor:
       if class_def.constructor.__code__.co_argcount == 0:
          def __init__(self, children=None, props={}, react_props=None):
              self.children = children
              self.native_props = props or {}
              self.props = react_props
              self.state = State()
              if react_props is not None: self.constructor()
          class_def.__init__  = __init__
       else:
          class Args: pass
          def init_rpython_component(self, children=None, props={}, react_props=None):
              self.children = children
              self.native_props = props or {}
              self.props = react_props
              self.state = State()
              if self.react_props is None: self.rpython_args = Args()
              #elif self.react_props['rpython_cache_id'].type != 'undefined':
              else: self.rpython_args = self.rpython_caches[self.react_props['rpython_cache_id'].toString()].args
          class_def.init_rpython_component  = init_rpython_component
          args = class_def.constructor.__code__.co_varnames
          defaults = class_def.constructor.__defaults__
          namespace = {key: value for key,value in zip(args, defaults)}
          indent = (' ' * 4) + '\n'
          code = 'def __init__(self, children=None, props={}, react_props=None, ' + ', '.join(arg + '=' + arg for arg in args) + '):'
          code += indent + 'self.init_rpython_component(children=children, props=props, react_props=react_props)'
          code += indent + 'if react_props is None: ' + ', '.join('self.rpython_args.' + arg  for arg in args) + ' = ' + ', '.join(arg for arg in args)
          code += indent + 'else: self.constructor(' + ', '.join(arg + '=self.rpython_args.' + arg for arg in args) + ')'
          exec(code, namespace)
          class_def.__init__ = namespace['__init__']
    #def create_component(children=None, props={}):
    #    component = Component(children=children, props=props) #.render
        #component.component = name
    #    component.function[0] = entry
    #    return component
    caches = {}
    @function
    def entry(props):
        variable = "rpython_react_component_count_" + str(custom_component_count)
        run_javascript("!('%s' in global) && (global.%s = -1)" % (variable, variable))
        object = Object("window.React.useState(function() {return {step: 0, id: ++global.%s}}).map(function (value, index, values) {return typeof value !== 'function' ? value : function () {return value({...values[0], step: values[0].step + 1})}})" % (variable))
        state, function = object['0'], object['1'].toFunction()
        step, id = state['step'].toInteger(), state['id'].toInteger()
        if step == 0:
           component = Component(children=Component.rpython_caches[props['rpython_cache_id'].toString()].children if props['rpython_cache_id'].type != 'undefined' else [], react_props=props)
           caches[id] = component
        component = caches[id]
        component.state_function = function
        return component.render().entry()
    Component.entry_function = (entry,)
    Component.rpython_count = {'count': 0}
    Component.rpython_caches = {}
    return Component

def is_type(value, type):
    if value == type: return True
    if isinstance(value, type): return True
    return False

def Component(class_def=None, State=None):
    if State and class_def is None:
       def wrapper(class_def):
           if not issubclass(class_def, ReactComponent):
              namespace = {'ReactRPythonComponent': ReactComponent}
              exec('class ' + class_def.__name__ + '(ReactRPythonComponent): pass', namespace)
              new_class = namespace[class_def.__name__]
              new_class.__dict__ = class_def.__dict__
              class_def = new_class
           return create_custom_component(class_def, State)
       return wrapper
    if State is None and class_def and issubclass(class_def, ReactComponent):
       class State: pass
       return create_custom_component(class_def, State)
    name = class_def.__name__
    props = {prop: getattr(class_def, prop) for prop in vars(class_def) if not prop.startswith('_')}
    indent = '\n' + (' ' * 4)
    json_props = ', '.join(["'{0}': {1} ".format(prop, prop if is_type(props[prop], types.str) else 'JSON.fromInt(%s)' % prop if is_type(props[prop], types.int) else 'JSON.fromFloat(%s)' % prop if is_type(props[prop], types.float) else 'JSON.fromBool(%s)' % prop if is_type(props[prop], types.bool) else 'JSON.fromList(%s)' % prop if is_type(props[prop], types.list) else 'JSON.fromTuple(%s)' % prop if is_type(props[prop], types.tuple) else prop + '.toRef()' if is_type(props[prop], Object) else 'JSON.fromFunction(%s)' % prop if is_type(props[prop], types.function) or is_type(props[prop], types.instancemethod) else 'JSON.fromDict(%s)' % prop if is_type(props[prop], types.dict) else 'None') for prop in props])
    code = 'def ' + name + '(children=None, props=None' + (' ,' if props else "") + ', '.join([prop + '=' + prop for prop in props]) + '):'
    code += indent + "rpython_props = {%s}" % (json_props)
    code += indent + "if props is not None:\n"
    code += ('    ' * 4 * 2) + "for key in props:\n"
    code += ('    ' * 4 * 3) + "if key not in rpython_props or JSON.isFalse(rpython_props[key]): rpython_props[key] = props[key]"
    code += indent + "rpython_component = RPYVARS['Component'](children=children, props=rpython_props)"
    code += indent + "rpython_component.component = RPYVARS['name']"
    code += indent + "return rpython_component"
    #code += indent + "createElement = RPYVARS['Object']('window.React.createElement')"
    #code += indent + "if children is None or not children: return createElement.call(RPYVARS['name'], JSON.fromDict(rpython_props))"
    #code += indent + "return createElement.call(RPYVARS['name'], JSON.fromDict(rpython_props), JSON.fromList([None if object is None else object.toRef() for object in children]))"
    known_types = [str, int, float, dict, list, tuple]
    for prop in props:
        props[prop] = props[prop]() if props[prop] in known_types else props[prop] if type(props[prop]) in known_types else None
    props.update({'RPYVARS': {'Object': Object, 'name': name, 'Component': ReactComponent}, 'JSON': JSON, 'rpytypes': types})
    exec(code, props)
    return props[name]

#children_cache = {}
object_cache = {}

def fromChildren(children, cache=True):
    refs = []
    for object in children:
        if object not in object_cache:
           object_cache[object] = None if object is None else object.entry().toRef()
        refs += [object_cache[object]]
    return JSON.fromList(refs)
    #if children in object_cache: return object_cache[children]
    #object = Object(
    #return JSON.fromList([None if object is None else object.entry().toRef() for object in children]) #)
    #object.render().toRef() if isinstance(object, ReactComponent)
    #object['rpython_variable'] = object.variable
    #if cache:
       #children_cache[object.variable] = children
       #object_cache[children] = object.toRef()
    #return object.toRef()

class ReactComponent:

    entry_function = (None,)
    component = None
    component_object = None
    rpython_count = {'count': 0}
    rpython_caches = {}

    def __init__(self, children=None, props={}, react_props=None):
        self.children = children
        self.native_props = props or {}
        self.props = react_props
        self.custom_render_function = (None,)
        return

    def mount(self):
        return

    def render(self):
        object = Object.fromString('This is the default RPython render text, override render method to get started')
        component = ReactComponent()
        component.component_object = object
        return component

    def entry(self):
        createElement = Object('window.React.createElement')
        if self.entry_function[0] is None:
            if self.component_object is not None: return self.component_object
            if self.component is None: return Object.fromString('This is the default RPython render text, override render method to get started')
            if self.children is None or not self.children: return createElement.call(self.component, JSON.fromDict(self.native_props))
            return createElement.call(self.component, JSON.fromDict(self.native_props), fromChildren(self.children, cache=False))
        #assert self.entry_function[0] is not None
        self.rpython_count['count'] += 1
        id = str(self.rpython_count['count'])
        self.rpython_caches[id] = self
        self.native_props['rpython_cache_id'] = id
        if self.children is None or not self.children: return createElement.call(JSON.fromFunction(self.entry_function[0]), JSON.fromDict(self.native_props))
        return createElement.call(JSON.fromFunction(self.entry_function[0]), JSON.fromDict(self.native_props), fromChildren(self.children))

    def setState(self):
        #if self.state_function is None: return
        self.state_function(JSON.fromDict({}))

    def toRef(self):
        #if isinstance(self, ReactComponent): return self.render().toRef()
        return self.entry().toRef()

def Text(text):
    component = ReactComponent()
    component.component_object = Object.fromString(text)
    return component

def get_component(name):
    def create_component(children=None, props={}):
        component = ReactComponent(children=children, props=props) #.render
        component.component = name
        #component.function[0] = entry
        return component
    #def entry(props):
    #    component = ReactComponent(children=children_cache[props['children']['rpython_variable'].toString()], react_props=props)
    #    return component.render()
    return create_component

def get_components(*names):
    if len(names) == 1: return get_component(name)
    components = []
    for name in names:
        components += [get_component(name)]
    return components
