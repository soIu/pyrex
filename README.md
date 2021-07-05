# Pyrex
Statically compiled React bindings in RPython, or a loosely transpiled in RapydScript

# Comparison
Here is a few comparison with Flutter widgets and React Components (JSX):

```dart
//Flutter

import 'package:flutter/material.dart';

class MyAppBar extends StatelessWidget {
  MyAppBar({required this.title});

  // Fields in a Widget subclass are always marked "final".

  final Widget title;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 56.0, // in logical pixels
      padding: const EdgeInsets.symmetric(horizontal: 8.0),
      decoration: BoxDecoration(color: Colors.blue[500]),
      // Row is a horizontal, linear layout.
      child: Row(
        // <Widget> is the type of items in the list.
        children: <Widget>[
          IconButton(
            icon: Icon(Icons.menu),
            tooltip: 'Navigation menu',
            onPressed: null, // null disables the button
          ),
          // Expanded expands its child
          // to fill the available space.
          Expanded(
            child: title,
          ),
          IconButton(
            icon: Icon(Icons.search),
            tooltip: 'Search',
            onPressed: null,
          ),
        ],
      ),
    );
  }
}
```

```javascript
//React

class Clock extends React.Component {
  constructor(props) {
    super(props);
    this.state = {date: new Date()};
  }

  componentDidMount() {
    this.timerID = setInterval(
      () => this.tick(),
      1000
    );
  }

  componentWillUnmount() {
    clearInterval(this.timerID);
  }

  tick() {
    this.setState({
      date: new Date()
    });
  }

  render() {
    return (
      <div>
        <h1>Hello, world!</h1>
        <h2>It is {this.state.date.toLocaleTimeString()}.</h2>
      </div>
    );
  }
}
```

```python
#Pyrex (in RPython)

from react import Component, Text
from react.components import Typography, IconButton, MoreVertical, Menu, MenuItem
from javascript import JSON, Object, function, types

@Component(path='Module.Admin.AppBar')
class AppBar:
    elevation = types.int

@Component
class span:
    className = types.ref

@Component
class div: pass

class Props: pass

@Component(Props=Props)
class Submenu:

    @function
    def onClick(setElement, event):
        setElement.call(event['currentTarget'].toRef())

    @function
    def onClose(setElement):
        setElement.call(None)

    @function
    def onMenu(setElement, menu):
        setElement.call(None)
        #Object.get('window', 'location')['hash'] = '#/' + menu['model'].toString()

    def render(self):
        menu = Object.get('Module')['orm_active_menu']
        if not menu.toBoolean() or not menu['childs']['length'].toInteger(): return div()
        id = 'solu-appbar-submenu'
        states = Object.get('window', 'React', 'useState').call(None)
        element, setElement = states['0'], states['1'] #.toFunction()
        return (
            div ([
                IconButton (props={'aria-controls': id, 'aria-haspopup': 'true', 'color': 'inherit'}, onClick=Object.createClosure(self.onClick, setElement).toRef(), children=[
                    MoreVertical ()
                ]),
                Menu (id=id, anchorEl=element.toRef(), keepMounted=True, open=element.toBoolean(), onClose=Object.createClosure(self.onClose, setElement).toRef(), children=[
                    MenuItem (props={'component': 'a', 'href': '#/' + child['model'].toString()}, onClick=Object.createClosure(self.onMenu, setElement, child).toRef(), children=[
                        Text (child['string'].toString())
                    ])
                for child in menu['childs'].toArray()])
            ])
        )
```

# Using for RapydScript or even on pure JS/TS (without JSX)
There's a RapydScript version that our team use to develop React Native apps (React Native doesn't yet support WebAssembly). It uses a babel [plugin](https://github.com/rafi16jan/babel-plugin-rapydscript) to load RapydScript code in a project that use babel as the loader.

```python
React = require('react')
Native = require('react-native')
StyleSheet = Native.StyleSheet

View, Text, StatusBar = require('pyrex').component(require('pyrex').kwargs(require('react-native'), 'View', 'Text'), require('expo-status-bar').StatusBar)

styles = StyleSheet.create({
    'container': {
        'flex': 1,
        'backgroundColor': "#fff",
        'alignItems': 'center',
        'justifyContent': 'center',
    }
})

def App():
    return (
        View (style=styles.container,
            Text ('Hello, this is from RapydScript!'),

        )
    )

module.exports = App
```

You can also use it from JS/TS without JSX, but it'll be more awkward

```javascript
//Bunch of importing things and other stuff...

class App extends React.Component {
  async stream() {
    try {
      if (!this.recorder) return;
      if (this.recorder.state === 'inactive') this.recorder.start();
      await sleep(0);
      const blob = await this.recorder.requestData();
      return this.stream();
    }
    catch (error) {
      console.error(error);
      return this.stream();
    }
  }
  unmutePlayers() {
    for (let user in this.state.users) this.state.users[user].ogvPlayer && (this.state.users[user].ogvPlayer.muted = this.state.unmute);
  }
  render () {
    const style = this.state.width > this.state.height ? {maxWidth: Object.keys(this.state.users).length > 0 ? 'calc(80vw - 24px)' : '100vw'} : {height: 'calc(100vh - 75px)'};
    if (!this.state.username) return div();
    return (
      div ({style: {display: 'flex'}},
        div ({style: {width: '20vw', margin: '2px'}}, ...Object.keys(this.state.users).map((user) =>
          div ({style: {}}, !this.state.users[user].Player ?
            video ({onProgress, onError: (event) => socket.emit('restart', user) && (delete self.state.users[user]) && self.setState(self.state), onClick, style: {'width': '20vw'}, autoplay: true, muted: !this.state.unmute, src: this.state.users[user].url}) :
            this.state.users[user].Player(),
            p (this.state.users[user].name)
          )), Object.keys(this.state.users).length > 0 &&
          div ( //{style: {display: 'none'}},
            input ({type: 'checkbox', name: 'mute', checked: !this.state.unmute, onClick: () => self.unmutePlayers() || self.setState({unmute: !this.state.unmute})}),
            label ({for: 'mute'}, 'Mute')
          )
        ),
        div ({style: {margin: '2px'}},
          (this.recorder && this.recorder.video) ?
          div ({ref: (ref) => ref && !ref.children.length && (this.recorder.video.onclick = onClick) && (this.recorder.video.onloadedmetadata = () => self.stream()) && ref.appendChild(this.recorder.video) && Object.keys(style).forEach(key => this.recorder.video.style[key] = style[key])}) :
          video ({onClick, style, muted: true, ref: (ref) => ref && (!ref.srcObject) &&  (ref.srcObject = console.log(self) || self.state.stream) && (ref.onloadedmetadata = () => ref.play() && self.stream())}),
          p (this.state.username)
        )
      )
    )
  }
}
```
