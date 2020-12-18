from javascript import JSON, Object, run_javascript

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

    def update(self):
        return

    def unmount(self):
        return

    def clean(self):
        self.state_function.release()

    def render(self):
        object = Object.fromString('This is the default RPython render text, override render method to get started')
        component = ReactComponent()
        component.component_object = object
        return component

    def entry(self):
        createElement = Object.get('window', 'React', 'createElement')
        if self.entry_function[0] is None:
            if self.component_object is not None: return self.component_object
            if self.component is None: return Object.fromString('This is the default RPython render text, override render method to get started')
            if self.component.startswith('RPYJSON:') and self.component.endswith(':RPYJSON'):
               path = JSON.parse_rpy_json(self.component)
               component = Object(path).keep()
               self.component = component.toRef()
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
        self.state_function.call(JSON.fromDict({}))

    def toRef(self):
        #if isinstance(self, ReactComponent): return self.render().toRef()
        return self.entry().toRef()
