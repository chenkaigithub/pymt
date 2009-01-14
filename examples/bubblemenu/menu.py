from pymt import *
import math

class MTBubbleWidget(MTWidget):
    def __init__(self, parent=None, pos=(0,0), color=(0.6,0.6,0.6,1.0), **kargs):
        self.x, self.y = pos
        self.color  = color
        img         = pyglet.image.load('menu-bubble.png')
        self.image  = pyglet.sprite.Sprite(img)
        assert self.image.width == self.image.height
        MTWidget.__init__(self,parent, **kargs)

        self._icon   = None

        # prepare animations
        self.anim_length = 10
        self.anim_precision = 1
        self.add_animation('show', 'scale', 1, self.anim_precision,
                           self.anim_length, func=AnimationAlpha.bubble)
        self.add_animation('show', 'opacity', 255, self.anim_precision, self.anim_length)
        self.add_animation('hide', 'scale', 0, self.anim_precision,
                           self.anim_length, func=AnimationAlpha.bubble)
        self.add_animation('hide', 'opacity', 0, self.anim_precision, self.anim_length)
        self.add_animation('show_all', 'scale', 1, self.anim_precision, self.anim_length, func=AnimationAlpha.ramp)
        self.add_animation('show_all', 'opacity', 255, self.anim_precision, self.anim_length)
        self.add_animation('hide_all', 'scale', 0, self.anim_precision, self.anim_length, func=AnimationAlpha.ramp)
        self.add_animation('hide_all', 'opacity', 0, self.anim_precision, self.anim_length)

    def draw(self):
        if not self.visible:
            return
        self.image.x = self.x - self.image.width / 2
        self.image.y = self.y - self.image.height / 2
        self.image.draw()
        if self.icon:
            self.icon.x = self.x - self.icon.width / 2
            self.icon.y = self.y - self.icon.height / 2
            self.icon.draw()

    def collidePoint(self, x, y):
        return Vector.distance(Vector(x, y), Vector(self.x, self.y)) < self.image.width / 2

    def show_all(self):
        MTWidget.show(self)
        self.start_animations('show_all')

    def hide_all(self):
        self.start_animations('hide_all')

    def on_animation_complete(self, anim):
        if anim.label == 'hide_all':
            MTWidget.hide(self)
        elif anim.label == 'hide':
            self.visible = False

    def show(self):
        self.visible = True
        self.opacity = 0
        self.scale = 0
        self.start_animations('show')

    def hide(self):
        self.opacity = 255
        self.scale = 1
        self.start_animations('hide')

    def _set_pos(self, pos):
        self.x, self.y = pos
    def _get_pos(self):
        return (self.x, self.y)
    pos = property(_get_pos, _set_pos)

    def _set_scale(self, scale):
        self.image.scale = scale
        if self.icon:
            self.icon.scale = scale
    def _get_scale(self):
        return self.image.scale
    scale = property(_get_scale, _set_scale)

    def _set_opacity(self, opacity):
        self.image.opacity = opacity
        if self.icon:
            self.icon.opacity = opacity
    def _get_opacity(self):
        return self.image.opacity
    opacity = property(_get_opacity, _set_opacity)

    def _set_width(self, width):
        self.image.width = width
    def _get_width(self):
        return self.image.width
    width = property(_get_width, _set_width)

    def _set_icon(self, icon):
        if icon is None:
            self._icon = None
        else:
            img = pyglet.image.load('icons/%s.png' % icon)
            self._icon = pyglet.sprite.Sprite(img)
    def _get_icon(self):
        return self._icon
    icon = property(_get_icon, _set_icon)

class MTMenuNode(MTBubbleWidget):
    STATE_ = 1

    def __init__(self, parent=None, pos=(0,0), size=30, color=(1,1,1,1)):
        MTBubbleWidget.__init__(self,
            parent=parent, pos=pos, color=color)
        self.pos = pos
        self.visible_children = False
        self.move_track = None
        self.move_action = False

    def add_widget(self, child):
        child.visible = False
        MTBubbleWidget.add_widget(self, child)

    def draw(self):
        if self.visible:
            MTBubbleWidget.draw(self)
        for c in self.children:
            if c.visible:
                c.dispatch_event('on_draw')

    def on_touch_down(self, touches, touchID, x, y):
        if self.visible and self.collidePoint(x, y) and self.move_track is None:
            self.move_track = touchID
            self.move_action = False

    def on_touch_move(self, touches, touchID, x, y):
        if self.move_track != touchID:
            return
        if self.pos == (x, y):
            return
        self.pos = (x, y)
        self.move_action = True

    def on_touch_up(self, touches, touchID, x, y):
        if self.move_track == touchID:
            self.move_track = None
            if self.move_action:
                return

        if self.visible_children:
            selected_child = None
            for c in self.children:
                if c.visible and c.collidePoint(x, y):
                    selected_child = c

            if selected_child is not None:
                selected_child.dispatch_event('on_touch_up', touches, touchID, x, y)
                self.select_child(selected_child)
                return True

        if self.visible and self.collidePoint(x, y):
            print 'click on', self.label
            if self.visible_children:
                self.close_children()
            else:
                self.open_children()
            return True

    def select_child(self, child):
        for c in self.children:
            if c != child:
                c.hide()
        #if self.parent:
        #   self.parent.hide()
        child.pos = self.pos

    def update_children_pos(self):
        max = len(self.children)
        i = 0
        start = math.pi / 2 # Orientation
        for c in self.children:
            x = self.x + math.sin(start + i * math.pi * 2 / max) * self.width
            y = self.y + math.cos(start + i * math.pi * 2 / max) * self.width
            c.pos = (x, y)
            i += 1

    def close_children(self):
        self.visible_children = False
        for c in self.children:
            c.hide(with_childs=True)

    def open_children(self):
        self.update_children_pos()
        self.visible_children = True
        for c in self.children:
            print 'show', c.label, c.x, c.y
            c.show()

    def hide(self, with_childs=False):
        MTBubbleWidget.hide(self)
        if with_childs:
            self.close_children()

    def _set_pos(self, pos):
        self.x, self.y = pos
        self.update_children_pos()
    def _get_pos(self):
        return (self.x, self.y)
    pos = property(_get_pos, _set_pos)


xmlmenu = """<?xml version="1.0"?>
<MTMenuNode label="'Menu'" icon="'glipper'" pos="(200,200)">
    <MTMenuNode label="'Applications'" icon="'disks'" color="(1,0,0,1)"/>
    <MTMenuNode label="'Settings'" icon="'nerolinux'" color="(0,1,0,1)">
        <MTMenuNode label="'Calibration'" color="(1,0,1,1)">
            <MTMenuNode label="'Applications'" icon="'disks'" color="(1,0,0,1)"/>
            <MTMenuNode label="'Settings'" icon="'nerolinux'" color="(0,1,0,1)">
                <MTMenuNode label="'Calibration'" icon="'znes'" color="(1,0,1,1)"/>
                <MTMenuNode label="'Background Color'" icon="'xpdf'" color="(1,1,0,1)"/>
            </MTMenuNode>
        </MTMenuNode>
        <MTMenuNode label="'Background Color'" icon="'xpdf'" color="(1,1,0,1)"/>
    </MTMenuNode>
    <MTMenuNode label="'Quit'" icon="'kfm'"/>
</MTMenuNode>
"""

if __name__ == '__main__':

    MTWidgetFactory.register('MTMenuNode', MTMenuNode)

    w = MTWindow(color=(0.16,0.223,0.313,1.0))
    #w.set_fullscreen()
    menu = XMLWidget(xml=xmlmenu)
    w.add_widget(menu)
    w.add_widget(MTDisplay())
    runTouchApp()
