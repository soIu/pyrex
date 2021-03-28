from .constructor import *
from .decorators import component_from_object
from javascript import JSON, Object, Function, function, asynchronous_function

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

from threading import Timer

def Method(get_component):

    def register_global():
        get_component.Component = get_component()

    Timer(1, register_global).start()

    def method(function, asynchronous=False, name=None, count=None): #Spread list of Object to each of the argument
        if asynchronous:
           def wrapper(function):
               return method(asynchronous_function(function), name=function.__name__, count=function.func_code.co_argcount)
           return wrapper
        if name is None: name = function.__name__
        if count is None: count = function.func_code.co_argcount
        count -= 1
        args = ', '.join(['self'] + ['args[%s]' % index for index in range(count)])
        arg_names = ', '.join(['self'] + ['rpyarg%s=None' % (index + 1) for index in range(count)] + ['args=None'])
        namespace = {'rpython_decorated_function': function, 'RPYObject': Object}
        indent = '\n' + (' ' * 4)
        code = 'def ' + name + '(' + arg_names + '):'
        #if count:
        code += indent + 'if args is None: return rpython_decorated_function(' + ', '.join(['self'] + ['rpyarg%s or RPYObject("null")' % (index + 1) for index in range(count)]) + ')'
        code += indent + 'if args is not None and len(args) < ' + str(count) + ': return rpython_decorated_function(' + ', '.join(['self'] + ['args[%s] if len(args) >= %s else RPYObject("null")' % (index, index + 1) for index in range(count)])  + ')'
        code += indent + 'assert args is not None and len(args) >= ' + str(count)
        code += indent + 'return rpython_decorated_function(' + args + ')'
        exec(code, namespace)
        function = namespace[name]
        return ReactMethod(function)

    methods = {}
    decorated_methods = {}

    class ReactMethod:
        method = (None,)
        cache = {'count': 0}

        def __init__(self, method):
            self.cache['count'] += 1
            count = self.cache['count']
            self.method = (method,)
            decorated_methods[self] = count
            methods[count] = self

    def fromMethod(component, method):
        function = component.state_function
        return Object.createClosure(handleMethod, function, component.props, Object.fromInteger(decorated_methods[method])).toRef()

    @Function
    def handleMethod(args):
        if args is None or len(args) < 3: return
        function = args[0]
        props = args[1]
        id = args[2]
        #props = function.call()
        method = methods[id.toInteger()]
        #component = object_cache[Component][props['rpython_cache_id'].toString()]
        #component.state_function._update()
        #if component.state_function.type == 'undefined':
        component = get_component.Component.Component(children=[component_from_object(children) for children in props['children'].toArray()] if props['children'].type == 'array' else [component_from_object(props['children'])] if props['children'].type == 'object' else [], react_props=props)
        component.state_function = function
        object_cache[get_component.Component][props['rpython_cache_id'].toString()] = component
        print get_component.Component
        props.log()
        print component
        print 'my key ' + props['rpython_cache_id'].toString()
        for key in object_cache[get_component.Component].cache:
            print key
            print object_cache[get_component.Component].cache[key]
        #component.props._update()
        #if component.props.type == 'undefined':
        #   component.props = props
        #component.init_constructor()
        Object.get('Module')['rpython_react_state_event'] = JSON.fromInteger(0)
        method.method[0](component, args=args[3:])
        #Object.get('Module')['rpython_react_state_event'] = None

    return fromMethod, method

def initial_state(component, initial=None):
    states = Object.get('Module', 'pyrex_state_cache')
    if states.type == 'undefined':
       Object.get('Module')['pyrex_state_cache'] = JSON.fromDict({})
       states = Object.get('Module', 'pyrex_state_cache')
    key = component.props['rpython_cache_id'].toString()
    state = states[key]
    if state.type == 'undefined':
       states[key] = Object('{}' if initial is None else initial, safe_json=True).toRef()
       state = states[key]
    return state

def unmount_state(component):
    states = Object.get('Module', 'pyrex_state_cache')
    if states.type == 'undefined':
       Object.get('Module')['pyrex_state_cache'] = JSON.fromDict({})
       states = Object.get('Module', 'pyrex_state_cache')
    key = component.props['rpython_cache_id'].toString()
    Object('delete Module.pyrex_state_cache[%s]' % key) #TODO Implement __del__ in Object
