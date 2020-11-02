from .constructor import *

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
